import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_text_event_returns_200_text_plain(page_client, archived_event, archived_compo):
    response = page_client.get(reverse("archive:text_event", args=[archived_event.id]))
    assert response.status_code == 200
    assert "text/plain" in response["Content-Type"]


@pytest.mark.django_db
def test_text_event_404_for_non_archived(page_client, non_archived_event):
    response = page_client.get(reverse("archive:text_event", args=[non_archived_event.id]))
    assert response.status_code == 404
