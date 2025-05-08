import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "navdb_manager.settings")

celery = Celery("navdb_manager")
celery.config_from_object("django.conf:settings", namespace="CELERY")
celery.autodiscover_tasks()
