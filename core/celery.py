import os

from celery import Celery
from celery.schedules import crontab
from kombu import Queue
from celery.schedules import schedule

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()




# Celery Beat schedule
app.conf.beat_schedule = {
    'check_worker_status': {
        'task': 'apps.render.tasks.check_worker_status',
        'schedule': crontab(minute='*'),
        'options': {
            'queue': 'check_worker_status',
        },
    },
}



app.conf.timezone = 'UTC'

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')