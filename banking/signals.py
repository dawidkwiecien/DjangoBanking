import logging
import os
import sys
import threading
import time
from datetime import timedelta

from django.db import connection, transaction
from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from banking.models import Account, Transfer

logger = logging.getLogger(__name__)

# How long a new transfer waits before each state change.
PROCESSING_AFTER = timedelta(seconds=5)
SETTLEMENT_AFTER = timedelta(seconds=20)

_worker_lock = threading.Lock()
_worker_started = False


@receiver(post_save, sender=Transfer, dispatch_uid="banking.queue_transfer")
def queue_transfer(sender, instance, created, **kwargs):
    if not created:
        return

    now = timezone.now()
    Transfer.objects.filter(pk=instance.pk).update(
        processing_at=now + PROCESSING_AFTER,
        realize_at=now + SETTLEMENT_AFTER,
    )
    logger.info(
        "Transfer %s accepted. Processing at %s, settles at %s",
        instance.pk,
        now + PROCESSING_AFTER,
        now + SETTLEMENT_AFTER,
    )


def advance_transfers():
    """Move due transfers through pending -> processing -> completed/rejected."""
    now = timezone.now()
    with transaction.atomic():
        due = list(
            Transfer.objects.select_for_update()
            .filter(status=Transfer.Status.PENDING, processing_at__lte=now)
            .order_by("pk")
        )
        for transfer in due:
            if transfer.realize_at and transfer.realize_at <= now:
                _book(transfer)
            else:
                transfer.status = Transfer.Status.PROCESSING
                transfer.save(update_fields=["status"])
                logger.info("Transfer %s is processing", transfer.pk)

        ready = list(
            Transfer.objects.select_for_update()
            .filter(status=Transfer.Status.PROCESSING, realize_at__lte=now)
            .order_by("pk")
        )
        for transfer in ready:
            _book(transfer)


def _book(transfer):
    if transfer.status not in (Transfer.Status.PENDING, Transfer.Status.PROCESSING):
        return

    account = Account.objects.select_for_update().get(pk=transfer.internalAccount_id)
    if transfer.ammount <= 0 or account.amount < transfer.ammount:
        transfer.status = Transfer.Status.REJECTED
        transfer.settled_at = timezone.now()
        transfer.save(update_fields=["status", "settled_at"])
        logger.info(
            "Rejected transfer %s on account %s",
            transfer.pk,
            transfer.internalAccount_id,
        )
        return

    Account.objects.filter(pk=account.pk).update(amount=F("amount") - transfer.ammount)
    transfer.status = Transfer.Status.COMPLETED
    transfer.settled_at = timezone.now()
    transfer.save(update_fields=["status", "settled_at"])
    logger.info(
        "Settled transfer %s on account %s",
        transfer.pk,
        transfer.internalAccount_id,
    )


def _settlement_loop():
    while True:
        try:
            advance_transfers()
        except Exception:
            logger.exception("Transfer settlement failed")
        finally:
            connection.close()
        time.sleep(1)


def start_settlement_worker():
    """Background clearer. Skips the autoreload parent and one-off commands."""
    global _worker_started

    if any(cmd in sys.argv for cmd in ("makemigrations", "migrate", "test", "shell")):
        return
    if "runserver" in sys.argv and os.environ.get("RUN_MAIN") != "true":
        return

    with _worker_lock:
        if _worker_started:
            return
        _worker_started = True

    threading.Thread(
        target=_settlement_loop,
        name="transfer-settlement",
        daemon=True,
    ).start()
    logger.info("Transfer settlement worker started")