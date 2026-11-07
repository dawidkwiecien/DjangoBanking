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
    owner = models.ManyToManyField(User,blank=True)

    def __str__(self):
                return self.number.__str__()

class Transfer(models.Model):
        class Status(models.TextChoices):
                PENDING = "pending", "Pending"
                PROCESSING = "processing", "Processing"
                COMPLETED = "completed", "Completed"
                REJECTED = "rejected", "Rejected"

        ammount = models.DecimalField(default=0)
        internalAccount = models.ForeignKey(Account, on_delete=models.CASCADE)
        externalAccount = models.CharField()
        status = models.CharField(
                max_length=16,
                choices=Status.choices,
                default=Status.PENDING,
        )
        created = models.DateTimeField(auto_now_add=True)
        processing_at = models.DateTimeField(null=True, blank=True)
        realize_at = models.DateTimeField(null=True, blank=True)
        settled_at = models.DateTimeField(null=True, blank=True)

        def save(self, *args, **kwargs):
                with transaction.atomic():
                        super().save(*args, **kwargs)

        def __str__(self):
                return f"{self.ammount} from {self.internalAccount_id} ({self.status})"