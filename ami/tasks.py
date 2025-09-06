# yourapp/tasks.py
from celery import shared_task
from .models import AuditSession

@shared_task
def update_audit_sessions_status():
    sessions = AuditSession.objects.exclude(status='SELESAI')
    for session in sessions:
        session.update_status()  # Pastikan method ini sudah ada di model