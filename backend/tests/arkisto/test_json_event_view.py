import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_json_event_returns_200_json(page_client, archived_event, archived_compo):
    response = page_client.get(reverse("archive:json_event", args=[archived_event.id]))
    assert response.status_code == 200
    assert response["Content-Type"] == "application/json"
    data = response.json()
    assert "entries" in data
    assert "compos" in data


@pytest.mark.django_db
def test_json_event_includes_compo_data(page_client, archived_event, archived_compo, archived_entry):
    response = page_client.get(reverse("archive:json_event", args=[archived_event.id]))
    data = response.json()
    assert len(data["compos"]) == 1
    assert data["compos"][0]["name"] == "Archived Compo"
    assert len(data["entries"]) == 1


@pytest.mark.django_db
def test_json_event_404_for_non_archived(page_client, non_archived_event):
    response = page_client.get(reverse("archive:json_event", args=[non_archived_event.id]))
    assert response.status_code == 404
