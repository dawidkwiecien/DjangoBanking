from django.apps import AppConfig


class BankingConfig(AppConfig):
    name = 'banking'
    def ready(self):
        from banking.signals import start_settlement_worker

        start_settlement_worker()