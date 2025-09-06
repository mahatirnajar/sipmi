# yourapp/management/commands/update_audit_status.py
from django.core.management.base import BaseCommand
from ami.models import AuditSession 

class Command(BaseCommand):
    help = 'Update status AuditSession based on current date'

    def handle(self, *args, **options):
        sessions = AuditSession.objects.exclude(status='SELESAI')
        updated = 0
        for session in sessions:
            old_status = session.status
            session.update_status()
            if session.status != old_status:
                updated += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Updated {session} from {old_status} to {session.status}')
                )
        self.stdout.write(self.style.SUCCESS(f'Total {updated} sessions updated.'))