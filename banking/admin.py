import logging

from django.contrib import admin, messages
from django.shortcuts import redirect

from banking.models import Account, Transfer

# Register your models here.
logger = logging.getLogger(__name__)

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    readonly_fields = [f.name for f in Account._meta.fields]
    list_display = ['number','amount','created']
    list_filter = ["owner"]

    def add_view(self, request, form_url=..., extra_context=...):
        account = Account.objects.create()

        self.message_user(
            request,
            f"Account {account.pk} was added",
            level=messages.SUCCESS,
        )

        return redirect(
            "admin:banking_account_changelist"
        )

@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "internalAccount",
        "amount",
        "externalAccount",
        "direction",
        "status",
    ]
    list_filter = ["status","direction"]
    readonly_fields = ["status","created"]