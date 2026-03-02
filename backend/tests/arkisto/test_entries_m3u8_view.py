import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_entries_m3u8_returns_200(page_client, archived_event, archived_compo):
    response = page_client.get(reverse("archive:entries_m3u8", args=[archived_event.id]))
    assert response.status_code == 200
    assert "text/plain" in response["Content-Type"]
    assert b"#EXTM3U" in response.content


@pytest.mark.django_db
def test_entries_m3u8_404_for_non_archived(page_client, non_archived_event):
    response = page_client.get(reverse("archive:entries_m3u8", args=[non_archived_event.id]))
    assert response.status_code == 404
