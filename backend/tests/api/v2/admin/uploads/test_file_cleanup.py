"""Tests for file cleanup in UploadedFileViewSet."""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from Instanssi.admin_upload.models import UploadedFile


def get_base_url(event_id: int) -> str:
    return f"/api/v2/admin/event/{event_id}/uploads/files/"


# django-cleanup uses on_commit() hooks, so transaction=True is required


@pytest.mark.django_db(transaction=True)
def test_old_file_deleted_when_replaced(staff_api_client, uploaded_file, test_zip):
    """When uploading a new file, the old file should be deleted from storage."""
    old_file_name = uploaded_file.file.name
    storage = uploaded_file.file.storage

    # Verify old file exists
    assert storage.exists(old_file_name)

    # Upload a new file
    new_file = SimpleUploadedFile("new_upload.zip", test_zip, content_type="application/zip")
    url = f"{get_base_url(uploaded_file.event_id)}{uploaded_file.id}/"
    response = staff_api_client.patch(url, {"file": new_file}, format="multipart")

    assert response.status_code == 200

    # Old file should be deleted
    assert not storage.exists(old_file_name)

    # New file should exist
    uploaded_file.refresh_from_db()
    assert storage.exists(uploaded_file.file.name)
    assert uploaded_file.file.name != old_file_name


@pytest.mark.django_db(transaction=True)
def test_file_deleted_when_instance_deleted(staff_api_client, uploaded_file):
    """When deleting an UploadedFile, the file should be deleted from storage."""
    file_name = uploaded_file.file.name
    storage = uploaded_file.file.storage

    # Verify file exists
    assert storage.exists(file_name)

    # Delete the instance
    url = f"{get_base_url(uploaded_file.event_id)}{uploaded_file.id}/"
    response = staff_api_client.delete(url)

    assert response.status_code == 204

    # File should be deleted from storage
    assert not storage.exists(file_name)

    # Instance should be deleted from database
    assert not UploadedFile.objects.filter(id=uploaded_file.id).exists()


@pytest.mark.django_db(transaction=True)
def test_file_not_deleted_when_other_fields_updated(staff_api_client, uploaded_file):
    """When updating non-file fields, the file should not be deleted."""
    file_name = uploaded_file.file.name
    storage = uploaded_file.file.storage

    # Verify file exists
    assert storage.exists(file_name)

    # Update only the description
    url = f"{get_base_url(uploaded_file.event_id)}{uploaded_file.id}/"
    response = staff_api_client.patch(url, {"description": "Updated description"}, format="multipart")

    assert response.status_code == 200

    # File should still exist
    assert storage.exists(file_name)

    # File name should not have changed
    uploaded_file.refresh_from_db()
    assert uploaded_file.file.name == file_name
