import os

from celery import Celery

from money_manager import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "money_manager.settings")

app = Celery("money_manager")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
