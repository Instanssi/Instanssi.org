from pathlib import Path

import pytest


def get_validate_url(event_id: int) -> str:
    return f"/api/v2/admin/event/{event_id}/kompomaatti/entries/validate-archive/"


@pytest.mark.django_db
def test_unauthenticated_returns_401(api_client, event):
    url = get_validate_url(event.id)
    response = api_client.get(url)
    assert response.status_code == 401


@pytest.mark.django_db
def test_user_without_permission_returns_403(user_api_client, event):
    url = get_validate_url(event.id)
    response = user_api_client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_returns_ok_with_count(staff_api_client, editable_compo_entry):
    url = get_validate_url(editable_compo_entry.compo.event_id)
    response = staff_api_client.get(url)
    assert response.status_code == 200
    assert response.data["ok"] is True
    assert response.data["count"] == 1


@pytest.mark.django_db
def test_count_excludes_disqualified_entries(staff_api_client, editable_compo_entry, votable_compo_entry):
    votable_compo_entry.disqualified = True
    votable_compo_entry.save()

    url = get_validate_url(editable_compo_entry.compo.event_id)
    response = staff_api_client.get(url)
    assert response.status_code == 200
    assert response.data["count"] == 1


@pytest.mark.django_db
def test_filter_by_compo(staff_api_client, editable_compo_entry, votable_compo_entry):
    url = get_validate_url(editable_compo_entry.compo.event_id)
    response = staff_api_client.get(url, {"compo": editable_compo_entry.compo_id})
    assert response.status_code == 200
    assert response.data["count"] == 1


@pytest.mark.django_db
def test_returns_zero_count_when_no_entries(staff_api_client, event):
    url = get_validate_url(event.id)
    response = staff_api_client.get(url)
    assert response.status_code == 200
    assert response.data["ok"] is True
    assert response.data["count"] == 0


@pytest.mark.django_db
def test_returns_400_when_file_missing(staff_api_client, editable_compo_entry):
    file_path = Path(editable_compo_entry.entryfile.path)
    file_path.unlink()

    url = get_validate_url(editable_compo_entry.compo.event_id)
    response = staff_api_client.get(url)
    assert response.status_code == 400
    assert "Missing entry files" in response.data["error"]
    assert len(response.data["entries"]) == 1


@pytest.mark.django_db
def test_returns_404_for_nonexistent_event(staff_api_client):
    url = get_validate_url(99999)
    response = staff_api_client.get(url)
    assert response.status_code == 404
