import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_video_index_returns_200(page_client, other_video):
    response = page_client.get(reverse("archive:video", args=[other_video.id]))
    assert response.status_code == 200
    assert "arkisto/video.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_video_index_404_for_non_archived(page_client, other_video_non_archived):
    response = page_client.get(reverse("archive:video", args=[other_video_non_archived.id]))
    assert response.status_code == 404


@pytest.mark.django_db
def test_video_index_404_for_nonexistent(page_client):
    response = page_client.get(reverse("archive:video", args=[99999]))
    assert response.status_code == 404
