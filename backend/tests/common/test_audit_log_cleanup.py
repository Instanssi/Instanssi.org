from datetime import timedelta

import pytest
from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from freezegun import freeze_time


@pytest.mark.django_db
@freeze_time("2026-03-05T12:00:00Z")
def test_cleanup_old_audit_logs_deletes_old_entries():
    """Audit log entries older than 6 months are deleted."""
    from Instanssi.common.tasks import cleanup_old_audit_logs

    ct = ContentType.objects.first()
    now = timezone.now()

    old_entry = LogEntry.objects.create(
        content_type=ct,
        object_id="1",
        object_repr="old",
        action=LogEntry.Action.UPDATE,
        timestamp=now - timedelta(days=181),
    )
    recent_entry = LogEntry.objects.create(
        content_type=ct,
        object_id="2",
        object_repr="recent",
        action=LogEntry.Action.UPDATE,
        timestamp=now - timedelta(days=179),
    )

    cleanup_old_audit_logs()

    assert not LogEntry.objects.filter(pk=old_entry.pk).exists()
    assert LogEntry.objects.filter(pk=recent_entry.pk).exists()


@pytest.mark.django_db
@freeze_time("2026-03-05T12:00:00Z")
def test_cleanup_old_audit_logs_no_entries():
    """Task runs without error when there are no entries."""
    from Instanssi.common.tasks import cleanup_old_audit_logs

    cleanup_old_audit_logs()
    assert LogEntry.objects.count() == 0
