from datetime import timedelta

from auditlog.models import LogEntry
from celery import shared_task
from django.utils import timezone


@shared_task  # type: ignore[untyped-decorator]
def cleanup_old_audit_logs() -> None:
    """Delete audit log entries older than 6 months for GDPR compliance."""
    cutoff = timezone.now() - timedelta(days=180)
    LogEntry.objects.filter(timestamp__lt=cutoff).delete()
