"""Tests for file cleanup in ProgramEventViewSet."""

from datetime import timedelta

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from Instanssi.ext_programme.models import ProgrammeEvent


def get_base_url(event_id: int) -> str:
    return f"/api/v2/admin/event/{event_id}/program/events/"


@pytest.fixture
def program_event_with_icons(event, test_image):
    """Program event with both icon fields set."""
    icon1 = SimpleUploadedFile("icon1.png", test_image, content_type="image/png")
    icon2 = SimpleUploadedFile("icon2.png", test_image, content_type="image/png")
    return ProgrammeEvent.objects.create(
        event=event,
        start=timezone.now() + timedelta(hours=1),
        end=timezone.now() + timedelta(hours=2),
        title="Test Event",
        description="Test description",
        icon_original=icon1,
        icon2_original=icon2,
        active=True,
    )


# django-cleanup uses on_commit() hooks, so transaction=True is required


@pytest.mark.django_db(transaction=True)
def test_old_icon_deleted_when_replaced(staff_api_client, program_event_with_icons, test_image):
    """When uploading a new icon, the old icon should be deleted from storage."""
    old_file_name = program_event_with_icons.icon_original.name
    storage = program_event_with_icons.icon_original.storage

    # Verify old file exists
    assert storage.exists(old_file_name)

    # Upload a new icon
    new_icon = SimpleUploadedFile("new_icon.png", test_image, content_type="image/png")
    url = f"{get_base_url(program_event_with_icons.event_id)}{program_event_with_icons.id}/"
    response = staff_api_client.patch(url, {"icon_original": new_icon}, format="multipart")

    assert response.status_code == 200

    # Old file should be deleted
    assert not storage.exists(old_file_name)

    # New file should exist
    program_event_with_icons.refresh_from_db()
    assert storage.exists(program_event_with_icons.icon_original.name)
    assert program_event_with_icons.icon_original.name != old_file_name


@pytest.mark.django_db(transaction=True)
def test_icon2_deleted_when_replaced(staff_api_client, program_event_with_icons, test_image):
    """When uploading a new icon2, the old icon2 should be deleted from storage."""
    old_file_name = program_event_with_icons.icon2_original.name
    storage = program_event_with_icons.icon2_original.storage

    # Verify old file exists
    assert storage.exists(old_file_name)

    # Upload a new icon2
    new_icon = SimpleUploadedFile("new_icon2.png", test_image, content_type="image/png")
    url = f"{get_base_url(program_event_with_icons.event_id)}{program_event_with_icons.id}/"
    response = staff_api_client.patch(url, {"icon2_original": new_icon}, format="multipart")

    assert response.status_code == 200

    # Old file should be deleted
    assert not storage.exists(old_file_name)

    # New file should exist
    program_event_with_icons.refresh_from_db()
    assert storage.exists(program_event_with_icons.icon2_original.name)
    assert program_event_with_icons.icon2_original.name != old_file_name


@pytest.mark.django_db(transaction=True)
def test_both_icons_deleted_when_instance_deleted(staff_api_client, program_event_with_icons):
    """When deleting a ProgrammeEvent, both icons should be deleted from storage."""
    icon1_name = program_event_with_icons.icon_original.name
    icon2_name = program_event_with_icons.icon2_original.name
    storage = program_event_with_icons.icon_original.storage
    item_id = program_event_with_icons.id

    # Verify both files exist
    assert storage.exists(icon1_name)
    assert storage.exists(icon2_name)

    # Delete the instance
    url = f"{get_base_url(program_event_with_icons.event_id)}{program_event_with_icons.id}/"
    response = staff_api_client.delete(url)

    assert response.status_code == 204

    # Both files should be deleted from storage
    assert not storage.exists(icon1_name)
    assert not storage.exists(icon2_name)

    # Instance should be deleted from database
    assert not ProgrammeEvent.objects.filter(id=item_id).exists()


@pytest.mark.django_db(transaction=True)
def test_icons_not_deleted_when_other_fields_updated(staff_api_client, program_event_with_icons):
    """When updating non-icon fields, the icons should not be deleted."""
    icon1_name = program_event_with_icons.icon_original.name
    icon2_name = program_event_with_icons.icon2_original.name
    storage = program_event_with_icons.icon_original.storage

    # Verify both files exist
    assert storage.exists(icon1_name)
    assert storage.exists(icon2_name)

    # Update only the title
    url = f"{get_base_url(program_event_with_icons.event_id)}{program_event_with_icons.id}/"
    response = staff_api_client.patch(url, {"title": "Updated Title"}, format="multipart")

    assert response.status_code == 200

    # Files should still exist
    assert storage.exists(icon1_name)
    assert storage.exists(icon2_name)

    # File names should not have changed
    program_event_with_icons.refresh_from_db()
    assert program_event_with_icons.icon_original.name == icon1_name
    assert program_event_with_icons.icon2_original.name == icon2_name
