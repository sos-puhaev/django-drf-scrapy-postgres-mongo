from django.apps import AppConfig
class BlsConfig(AppConfig):
    name = 'bls'

    def ready(self):
        from .views.cron_method import start_scheduler
        start_scheduler()