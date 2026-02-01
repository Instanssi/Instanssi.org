"""Tests for file cleanup in CompoEntryViewSet."""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from Instanssi.kompomaatti.models import Entry


def get_base_url(event_id: int) -> str:
    return f"/api/v2/admin/event/{event_id}/kompomaatti/entries/"


# django-cleanup uses on_commit() hooks, so transaction=True is required


@pytest.mark.django_db(transaction=True)
def test_old_entryfile_deleted_when_replaced(staff_api_client, editable_compo_entry, test_zip):
    """When uploading a new entryfile, the old file should be deleted from storage."""
    old_file_name = editable_compo_entry.entryfile.name
    storage = editable_compo_entry.entryfile.storage

    # Verify old file exists
    assert storage.exists(old_file_name)

    # Upload a new file
    new_file = SimpleUploadedFile("new_entry.zip", test_zip, content_type="application/zip")
    url = f"{get_base_url(editable_compo_entry.compo.event_id)}{editable_compo_entry.id}/"
    response = staff_api_client.patch(url, {"entryfile": new_file}, format="multipart")

    assert response.status_code == 200

    # Old file should be deleted
    assert not storage.exists(old_file_name)

    # New file should exist
    editable_compo_entry.refresh_from_db()
    assert storage.exists(editable_compo_entry.entryfile.name)
    assert editable_compo_entry.entryfile.name != old_file_name


@pytest.mark.django_db(transaction=True)
def test_old_sourcefile_deleted_when_replaced(staff_api_client, editable_compo_entry, test_zip):
    """When uploading a new sourcefile, the old file should be deleted from storage."""
    old_file_name = editable_compo_entry.sourcefile.name
    storage = editable_compo_entry.sourcefile.storage

    # Verify old file exists
    assert storage.exists(old_file_name)

    # Upload a new file
    new_file = SimpleUploadedFile("new_source.zip", test_zip, content_type="application/zip")
    url = f"{get_base_url(editable_compo_entry.compo.event_id)}{editable_compo_entry.id}/"
    response = staff_api_client.patch(url, {"sourcefile": new_file}, format="multipart")

    assert response.status_code == 200

    # Old file should be deleted
    assert not storage.exists(old_file_name)

    # New file should exist
    editable_compo_entry.refresh_from_db()
    assert storage.exists(editable_compo_entry.sourcefile.name)
    assert editable_compo_entry.sourcefile.name != old_file_name


@pytest.mark.django_db(transaction=True)
def test_old_imagefile_deleted_when_replaced(staff_api_client, editable_compo_entry, test_image):
    """When uploading a new imagefile, the old file should be deleted from storage."""
    old_file_name = editable_compo_entry.imagefile_original.name
    storage = editable_compo_entry.imagefile_original.storage

    # Verify old file exists
    assert storage.exists(old_file_name)

    # Upload a new file
    new_file = SimpleUploadedFile("new_image.png", test_image, content_type="image/png")
    url = f"{get_base_url(editable_compo_entry.compo.event_id)}{editable_compo_entry.id}/"
    response = staff_api_client.patch(url, {"imagefile_original": new_file}, format="multipart")

    assert response.status_code == 200

    # Old file should be deleted
    assert not storage.exists(old_file_name)

    # New file should exist
    editable_compo_entry.refresh_from_db()
    assert storage.exists(editable_compo_entry.imagefile_original.name)
    assert editable_compo_entry.imagefile_original.name != old_file_name


@pytest.mark.django_db(transaction=True)
def test_sourcefile_cleared_when_empty_string_sent(staff_api_client, editable_compo_entry):
    """When sending empty string for sourcefile, the file should be cleared and deleted."""
    old_file_name = editable_compo_entry.sourcefile.name
    storage = editable_compo_entry.sourcefile.storage

    # Verify old file exists
    assert storage.exists(old_file_name)

    # Clear the sourcefile
    url = f"{get_base_url(editable_compo_entry.compo.event_id)}{editable_compo_entry.id}/"
    response = staff_api_client.patch(url, {"sourcefile": ""}, format="multipart")

    assert response.status_code == 200

    # Old file should be deleted
    assert not storage.exists(old_file_name)

    # Sourcefile field should be empty
    editable_compo_entry.refresh_from_db()
    assert not editable_compo_entry.sourcefile


@pytest.mark.django_db(transaction=True)
def test_imagefile_cleared_when_empty_string_sent(staff_api_client, editable_compo_entry):
    """When sending empty string for imagefile, the file should be cleared and deleted."""
    # First, set the compo to allow optional images
    editable_compo_entry.compo.thumbnail_pref = 2  # Optional
    editable_compo_entry.compo.save()

    old_file_name = editable_compo_entry.imagefile_original.name
    storage = editable_compo_entry.imagefile_original.storage

    # Verify old file exists
    assert storage.exists(old_file_name)

    # Clear the imagefile
    url = f"{get_base_url(editable_compo_entry.compo.event_id)}{editable_compo_entry.id}/"
    response = staff_api_client.patch(url, {"imagefile_original": ""}, format="multipart")

    assert response.status_code == 200

    # Old file should be deleted
    assert not storage.exists(old_file_name)

    # Imagefile field should be empty
    editable_compo_entry.refresh_from_db()
    assert not editable_compo_entry.imagefile_original


@pytest.mark.django_db(transaction=True)
def test_all_files_deleted_when_instance_deleted(staff_api_client, editable_compo_entry):
    """When deleting an Entry, all files should be deleted from storage."""
    entryfile_name = editable_compo_entry.entryfile.name
    sourcefile_name = editable_compo_entry.sourcefile.name
    imagefile_name = editable_compo_entry.imagefile_original.name
    storage = editable_compo_entry.entryfile.storage
    entry_id = editable_compo_entry.id

    # Verify all files exist
    assert storage.exists(entryfile_name)
    assert storage.exists(sourcefile_name)
    assert storage.exists(imagefile_name)

    # Delete the instance
    url = f"{get_base_url(editable_compo_entry.compo.event_id)}{editable_compo_entry.id}/"
    response = staff_api_client.delete(url)

    assert response.status_code == 204

    # All files should be deleted from storage
    assert not storage.exists(entryfile_name)
    assert not storage.exists(sourcefile_name)
    assert not storage.exists(imagefile_name)

    # Instance should be deleted from database
    assert not Entry.objects.filter(id=entry_id).exists()


@pytest.mark.django_db(transaction=True)
def test_files_not_deleted_when_other_fields_updated(staff_api_client, editable_compo_entry):
    """When updating non-file fields, the files should not be deleted."""
    entryfile_name = editable_compo_entry.entryfile.name
    sourcefile_name = editable_compo_entry.sourcefile.name
    imagefile_name = editable_compo_entry.imagefile_original.name
    storage = editable_compo_entry.entryfile.storage

    # Verify all files exist
    assert storage.exists(entryfile_name)
    assert storage.exists(sourcefile_name)
    assert storage.exists(imagefile_name)

    # Update only the name
    url = f"{get_base_url(editable_compo_entry.compo.event_id)}{editable_compo_entry.id}/"
    response = staff_api_client.patch(url, {"name": "Updated Name"}, format="multipart")

    assert response.status_code == 200

    # All files should still exist
    assert storage.exists(entryfile_name)
    assert storage.exists(sourcefile_name)
    assert storage.exists(imagefile_name)

    # File names should not have changed
    editable_compo_entry.refresh_from_db()
    assert editable_compo_entry.entryfile.name == entryfile_name
    assert editable_compo_entry.sourcefile.name == sourcefile_name
    assert editable_compo_entry.imagefile_original.name == imagefile_name
