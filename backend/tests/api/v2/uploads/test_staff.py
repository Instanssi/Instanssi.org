import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/uploads/files/"


@pytest.mark.django_db
def test_staff_can_list_uploaded_files(staff_api_client, uploaded_file):
    """Test that staff can list all uploaded files."""
    base_url = get_base_url(uploaded_file.event_id)
    req = staff_api_client.get(base_url)
    assert req.status_code == 200
    assert len(req.data) >= 1


@pytest.mark.django_db
def test_staff_can_get_uploaded_file_detail(staff_api_client, uploaded_file):
    """Test that staff can get uploaded file details."""
    base_url = get_base_url(uploaded_file.event_id)
    req = staff_api_client.get(f"{base_url}{uploaded_file.id}/")
    assert req.status_code == 200
    assert req.data == {
        "id": uploaded_file.id,
        "event": uploaded_file.event_id,
        "user": uploaded_file.user_id,
        "description": uploaded_file.description,
        "file": req.data["file"],  # Dynamic path
        "file_url": req.data["file_url"],  # Dynamic URL
        "filename": uploaded_file.name(),
        "date": uploaded_file.date.astimezone(settings.ZONE_INFO).isoformat(),
    }
    assert req.data["file"] is not None
    assert req.data["file_url"] is not None


@pytest.mark.django_db
def test_staff_can_create_uploaded_file(staff_api_client, event, staff_user, test_zip):
    """Test that staff can create a new uploaded file."""
    base_url = get_base_url(event.id)
    file = SimpleUploadedFile("new_upload.zip", test_zip, content_type="application/zip")
    req = staff_api_client.post(
        base_url,
        {
            "user": staff_user.id,
            "description": "New uploaded file",
            "file": file,
        },
        format="multipart",
    )
    assert req.status_code == 201
    assert req.data == {
        "id": req.data["id"],
        "event": event.id,  # Set from URL
        "user": staff_user.id,
        "description": "New uploaded file",
        "file": req.data["file"],  # Dynamic path
        "file_url": req.data["file_url"],  # Dynamic URL
        "filename": req.data["filename"],  # Dynamic filename with timestamp
        "date": req.data["date"],  # Dynamic timestamp
    }
    assert req.data["file"] is not None
    assert req.data["file_url"] is not None
    assert "new_upload" in req.data["filename"]


@pytest.mark.django_db
def test_staff_can_update_uploaded_file(staff_api_client, uploaded_file):
    """Test that staff can update an uploaded file."""
    base_url = get_base_url(uploaded_file.event_id)
    req = staff_api_client.patch(f"{base_url}{uploaded_file.id}/", {"description": "Updated description"})
    assert req.status_code == 200
    assert req.data == {
        "id": uploaded_file.id,
        "event": uploaded_file.event_id,
        "user": uploaded_file.user_id,
        "description": "Updated description",
        "file": req.data["file"],  # Dynamic path
        "file_url": req.data["file_url"],  # Dynamic URL
        "filename": uploaded_file.name(),
        "date": uploaded_file.date.astimezone(settings.ZONE_INFO).isoformat(),
    }


@pytest.mark.django_db
def test_staff_can_delete_uploaded_file(staff_api_client, uploaded_file):
    """Test that staff can delete an uploaded file."""
    base_url = get_base_url(uploaded_file.event_id)
    req = staff_api_client.delete(f"{base_url}{uploaded_file.id}/")
    assert req.status_code == 204


@pytest.mark.django_db
def test_filter_by_event(staff_api_client, event, uploaded_file, other_event_uploaded_file):
    """Test that uploaded files are filtered by event."""
    base_url = get_base_url(event.id)
    req = staff_api_client.get(base_url)
    assert req.status_code == 200
    # Should only see files from this event
    for uf in req.data:
        assert uf["event"] == event.id
    # Verify the other event's file is not included
    ids = [uf["id"] for uf in req.data]
    assert other_event_uploaded_file.id not in ids


@pytest.mark.django_db
def test_filter_by_user(staff_api_client, uploaded_file, staff_user):
    """Test filtering uploaded files by user."""
    base_url = get_base_url(uploaded_file.event_id)
    req = staff_api_client.get(f"{base_url}?user={staff_user.id}")
    assert req.status_code == 200
    for uf in req.data:
        assert uf["user"] == staff_user.id


@pytest.mark.django_db
def test_search_by_description(staff_api_client, uploaded_file):
    """Test searching uploaded files by description."""
    base_url = get_base_url(uploaded_file.event_id)
    # Get a word from the description to search for
    search_term = uploaded_file.description.split()[0]
    req = staff_api_client.get(f"{base_url}?search={search_term}")
    assert req.status_code == 200
    assert len(req.data) >= 1


@pytest.mark.django_db
def test_ordering_by_date(staff_api_client, event, staff_user, test_zip):
    """Test that uploaded files are ordered by date (newest first) by default."""
    base_url = get_base_url(event.id)
    # Create multiple files
    from Instanssi.admin_upload.models import UploadedFile

    for i in range(3):
        file = SimpleUploadedFile(f"file_{i}.zip", test_zip, content_type="application/zip")
        UploadedFile.objects.create(
            event=event,
            user=staff_user,
            description=f"Test file {i}",
            file=file,
        )

    req = staff_api_client.get(base_url)
    assert req.status_code == 200
    # Check that dates are in descending order (newest first)
    dates = [uf["date"] for uf in req.data]
    assert dates == sorted(dates, reverse=True)
