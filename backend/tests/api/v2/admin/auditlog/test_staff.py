"""Tests for staff access to the audit log endpoint."""

import pytest
from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType

from Instanssi.kompomaatti.models import Event

BASE_URL = "/api/v2/admin/auditlog/"


@pytest.fixture
def log_entry(event, super_user):
    """Create a log entry for testing."""
    content_type = ContentType.objects.get_for_model(Event)
    return LogEntry.objects.create(
        content_type=content_type,
        object_pk=str(event.pk),
        object_id=event.pk,
        object_repr=str(event),
        action=LogEntry.Action.UPDATE,
        changes='{"name": ["Old Name", "New Name"]}',
        actor=super_user,
    )


@pytest.mark.django_db
def test_auditlog_list(super_api_client, log_entry):
    """Test GET for all items."""
    result = super_api_client.get(BASE_URL)
    assert result.status_code == 200
    # LimitOffsetPagination returns list when no limit specified
    assert len(result.data) >= 1


@pytest.mark.django_db
def test_auditlog_list_empty(super_api_client):
    """Test GET when no log entries exist."""
    result = super_api_client.get(BASE_URL)
    assert result.status_code == 200
    assert result.data == []


@pytest.mark.django_db
def test_auditlog_list_paginated(super_api_client, log_entry):
    """Test GET with pagination parameters."""
    result = super_api_client.get(BASE_URL, {"limit": 10, "offset": 0})
    assert result.status_code == 200
    assert "count" in result.data
    assert "results" in result.data
    assert result.data["count"] >= 1


@pytest.mark.django_db
def test_auditlog_detail(super_api_client, log_entry):
    """Test GET for specific ID."""
    result = super_api_client.get(f"{BASE_URL}{log_entry.id}/")
    assert result.status_code == 200
    assert result.data["id"] == log_entry.id
    assert result.data["object_pk"] == str(log_entry.object_pk)
    assert result.data["action"] == LogEntry.Action.UPDATE


@pytest.mark.django_db
def test_auditlog_filter_by_content_type(super_api_client, log_entry, event):
    """Test filtering by app_label and model."""
    result = super_api_client.get(BASE_URL, {"app_label": "kompomaatti", "model": "event"})
    assert result.status_code == 200
    assert len(result.data) >= 1
    # Verify all results are for the correct content type
    for entry in result.data:
        assert entry["content_type"]["app_label"] == "kompomaatti"
        assert entry["content_type"]["model"] == "event"


@pytest.mark.django_db
def test_auditlog_filter_by_object_pk(super_api_client, log_entry, event):
    """Test filtering by object_pk."""
    result = super_api_client.get(BASE_URL, {"object_pk": str(event.pk)})
    assert result.status_code == 200
    assert len(result.data) >= 1
    for entry in result.data:
        assert entry["object_pk"] == str(event.pk)


@pytest.mark.django_db
def test_auditlog_filter_by_nonexistent_content_type(super_api_client, log_entry):
    """Test filtering by nonexistent content type returns empty."""
    result = super_api_client.get(BASE_URL, {"app_label": "nonexistent", "model": "model"})
    assert result.status_code == 200
    assert len(result.data) == 0


@pytest.mark.django_db
def test_auditlog_response_format(super_api_client, log_entry):
    """Test that response includes expected fields."""
    result = super_api_client.get(f"{BASE_URL}{log_entry.id}/")
    assert result.status_code == 200
    data = result.data
    # Check required fields
    assert "id" in data
    assert "content_type" in data
    assert "object_pk" in data
    assert "object_repr" in data
    assert "action" in data
    assert "changes" in data
    assert "timestamp" in data
    assert "actor" in data
    assert "remote_addr" in data
    # Check nested content_type structure
    assert "app_label" in data["content_type"]
    assert "model" in data["content_type"]
    # Check nested actor structure
    assert "id" in data["actor"]
    assert "username" in data["actor"]


@pytest.mark.django_db
def test_auditlog_is_read_only(super_api_client, log_entry):
    """Test that POST, PUT, PATCH, DELETE are not allowed."""
    # POST
    result = super_api_client.post(BASE_URL, {})
    assert result.status_code == 405

    # PUT
    result = super_api_client.put(f"{BASE_URL}{log_entry.id}/", {})
    assert result.status_code == 405

    # PATCH
    result = super_api_client.patch(f"{BASE_URL}{log_entry.id}/", {})
    assert result.status_code == 405

    # DELETE
    result = super_api_client.delete(f"{BASE_URL}{log_entry.id}/")
    assert result.status_code == 405


@pytest.mark.django_db
def test_auditlog_ordering_default(super_api_client, event, super_user):
    """Test that entries are ordered by timestamp descending by default."""
    content_type = ContentType.objects.get_for_model(Event)
    # Create multiple entries
    entry1 = LogEntry.objects.create(
        content_type=content_type,
        object_pk=str(event.pk),
        object_repr="Entry 1",
        action=LogEntry.Action.CREATE,
        actor=super_user,
    )
    entry2 = LogEntry.objects.create(
        content_type=content_type,
        object_pk=str(event.pk),
        object_repr="Entry 2",
        action=LogEntry.Action.UPDATE,
        actor=super_user,
    )

    result = super_api_client.get(BASE_URL)
    assert result.status_code == 200
    results = result.data
    # Most recent should be first
    assert results[0]["id"] == entry2.id
    assert results[1]["id"] == entry1.id


@pytest.mark.django_db
def test_auditlog_permission_filtering_for_non_superuser(staff_api_client, log_entry, event, staff_user):
    """Test that non-superuser only sees entries for models they have view permission for.

    staff_user doesn't have auditlog.view_logentry permission, so should get 403.
    """
    result = staff_api_client.get(BASE_URL)
    assert result.status_code == 403
