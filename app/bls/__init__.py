from django.apps import apps

def ready():
    BlsConfig = apps.get_app_config('bls')
    BlsConfig.ready()

default_app_config = 'bls.apps.BlsConfig'