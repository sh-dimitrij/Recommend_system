# rec_core/apps.py
from django.apps import AppConfig

class RecCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rec_core'
    
    def ready(self):
        import rec_core.signals

