# sipmi/celery.py
import os
from celery import Celery

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sipmi.settings')

app = Celery('sipmi')

# Load config from Django settings, dengan namespace 'CELERY'
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto discover tasks.py di semua registered apps
app.autodiscover_tasks()