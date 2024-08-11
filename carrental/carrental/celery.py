from __future__ import absolute_import, unicode_literals
import os


from celery import Celery
from django.conf import settings
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carrental.settings')


app = Celery('carrental')
app.conf.enable_utc = False

app.conf.update(timezone = 'Asia/Kolkata')

# Using a string here means the worker doesn't have to serialize# the configuration object to child processes.# - namespace='CELERY' means all celery-related configuration keys#   should have a `CELERY_` prefix.
app.config_from_object(settings, namespace='CELERY')

# Load task modules from all registered Django apps.# Celery Beat tasks registration


# Celery Beat Settings

# app.conf.beat_schedule = {
    # 'send-mail-every-day-at-8': {
        # 'task': 'car.tasks.send_mail_func',
        # 'schedule': crontab(hour=17, minute=16),
        # 'args': (2, )
    # }
# }

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


# celery -A carrental.celery worker --pool=solo -l info
# celery -A carrental worker -l info --beat --scheduler django