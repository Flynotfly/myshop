import os
from celery import Celery


# set default Django settings module for the 'celery' program.
os.environ.setdefault('django.conf:settings', 'myshop.settings')

app = Celery('myshop')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
