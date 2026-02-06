import zipfile
from io import BytesIO
from pathlib import Path

import pytest


def get_archive_url(event_id: int) -> str:
    return f"/api/v2/admin/event/{event_id}/kompomaatti/entries/download-archive/"


@pytest.mark.django_db
def test_unauthenticated_returns_401(api_client, event):
    url = get_archive_url(event.id)
    response = api_client.get(url)
    assert response.status_code == 401


@pytest.mark.django_db
def test_user_without_permission_returns_403(user_api_client, event):
    url = get_archive_url(event.id)
    response = user_api_client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_returns_zip_content_type(staff_api_client, editable_compo_entry):
    url = get_archive_url(editable_compo_entry.compo.event_id)
    response = staff_api_client.get(url)
    assert response.status_code == 200
    assert response["Content-Type"] == "application/zip"


@pytest.mark.django_db
def test_returns_attachment_disposition(staff_api_client, editable_compo_entry):
    url = get_archive_url(editable_compo_entry.compo.event_id)
    response = staff_api_client.get(url)
    assert response.status_code == 200
    assert "attachment" in response["Content-Disposition"]
    assert ".zip" in response["Content-Disposition"]


@pytest.mark.django_db
def test_archive_contains_entry_file(staff_api_client, editable_compo_entry):
    url = get_archive_url(editable_compo_entry.compo.event_id)
    response = staff_api_client.get(url)
    assert response.status_code == 200

    content = b"".join(response.streaming_content)
    with zipfile.ZipFile(BytesIO(content)) as zf:
        names = zf.namelist()

    assert len(names) == 1
    assert "001__" in names[0]


@pytest.mark.django_db
def test_archive_excludes_disqualified_entries(staff_api_client, editable_compo_entry, votable_compo_entry):
    votable_compo_entry.disqualified = True
    votable_compo_entry.save()

    url = get_archive_url(editable_compo_entry.compo.event_id)
    response = staff_api_client.get(url)
    assert response.status_code == 200

    content = b"".join(response.streaming_content)
    with zipfile.ZipFile(BytesIO(content)) as zf:
        names = zf.namelist()

    assert len(names) == 1


@pytest.mark.django_db
def test_filter_by_compo(staff_api_client, editable_compo_entry, votable_compo_entry):
    url = get_archive_url(editable_compo_entry.compo.event_id)
    response = staff_api_client.get(url, {"compo": editable_compo_entry.compo_id})
    assert response.status_code == 200

    content = b"".join(response.streaming_content)
    with zipfile.ZipFile(BytesIO(content)) as zf:
        names = zf.namelist()

    assert len(names) == 1


@pytest.mark.django_db
def test_empty_archive_when_no_entries(staff_api_client, event):
    url = get_archive_url(event.id)
    response = staff_api_client.get(url)
    assert response.status_code == 200

    content = b"".join(response.streaming_content)
    with zipfile.ZipFile(BytesIO(content)) as zf:
        names = zf.namelist()

    assert len(names) == 0


@pytest.mark.django_db
def test_archive_uses_rank_prefix(staff_api_client, closed_compo_entry):
    url = get_archive_url(closed_compo_entry.compo.event_id)
    response = staff_api_client.get(url)
    assert response.status_code == 200

    content = b"".join(response.streaming_content)
    with zipfile.ZipFile(BytesIO(content)) as zf:
        names = zf.namelist()

    assert len(names) == 1
    assert names[0].startswith("closed_compo/001__")


@pytest.mark.django_db
def test_returns_400_when_file_missing(staff_api_client, editable_compo_entry):
    file_path = Path(editable_compo_entry.entryfile.path)
    file_path.unlink()

    url = get_archive_url(editable_compo_entry.compo.event_id)
    response = staff_api_client.get(url)
    assert response.status_code == 400
    assert "Missing entry files" in response.data["error"]
    assert len(response.data["entries"]) == 1
