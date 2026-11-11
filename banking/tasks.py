from crontask import cron
from django.utils import timezone
from django.db.models import F
from django.db import transaction
from django.tasks import task

from banking.models import Account, Transfer, TransferDirection, TransferStatus
import logging
logger = logging.getLogger(__name__)

@cron("*/1 * * * *")  # every 5 minutes
@task
def send_Transfers():
    with transaction.atomic():
            now = timezone.now()
            due = list(
                Transfer.objects.select_for_update()
                .filter(status=TransferStatus.PENDING, created__lte=now)
                .order_by("pk")
            )
            for transfer in due:
                logger.info(transfer.id)
                account = Account.objects.select_for_update().get(pk=transfer.internalAccount_id)
                if transfer.direction == TransferDirection.INCOMING:
                    Account.objects.filter(pk=account.pk).update(amount=F("amount") + transfer.amount)
                    transfer.status = TransferStatus.COMPLETED
                    transfer.save(update_fields=["status"])
                    logger.info("Incoming")
                elif transfer.direction == TransferDirection.OUTGOING:
                    if transfer.amount <= 0 or account.amount < transfer.amount:
                        transfer.status = TransferStatus.REJECTED
                        transfer.save(update_fields=["status"])
                        logger.info(
                            "Rejected transfer %s on account %s",
                            transfer.pk,
                            transfer.internalAccount_id,
                        )
                        return
                
                    Account.objects.filter(pk=account.pk).update(amount=F("amount") - transfer.amount)
                    transfer.status = TransferStatus.COMPLETED
                    transfer.save(update_fields=["status"])
                    logger.info(
                        "Settled transfer %s on account %s",
                        transfer.pk,
                        transfer.internalAccount_id,
                    )
                elif transfer.direction == TransferDirection.INTERNAL:
                    logger.info("Internal")
                else:
                    logger.error("Transfer type not found")
                    