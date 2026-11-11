from django.db import models, transaction
from django.db.models.functions import Now
from banking.utils import generateAccount
from django.contrib.auth.models import User


# Create your models here.

class Account(models.Model):
    number = models.CharField(max_length=34, primary_key=True, default=generateAccount)
    amount = models.DecimalField(default=0)
    name = models.CharField(default="New account")
    created = models.DateTimeField(db_default=Now())
    owner = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.number.__str__()


class TransferStatus(models.IntegerChoices):
    PENDING = 0, "Pending"
    PROCESSING = 1, "Processing"
    COMPLETED = 2, "Completed"
    REJECTED = 3, "Rejected"


class TransferDirection(models.IntegerChoices):
    INCOMING = 0, "Incoming",
    OUTGOING = 1, "Outgoing",
    INTERNAL = 2, "Internal"




class Transfer(models.Model):
    amount = models.DecimalField(default=0)
    internalAccount = models.ForeignKey(Account, on_delete=models.CASCADE)
    externalAccount = models.CharField()
    status = models.IntegerField(
        choices=TransferStatus.choices,
        default=TransferStatus.PENDING,
    )
    direction = models.IntegerField(choices=TransferDirection.choices, default=TransferDirection.INTERNAL)
    created = models.DateTimeField(db_default=Now())

    def save(self, *args, **kwargs):
        with transaction.atomic():
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.amount} from {self.internalAccount} ({self.status})"

class TransferHistory(models.Model):
    #transfer = models.ForeignKey(Transfer, on_delete=models.CASCADE)
    date = models.DateTimeField(db_default=Now())
    status = models.IntegerField(
        choices=TransferStatus.choices,
        default=TransferStatus.PENDING,
    )