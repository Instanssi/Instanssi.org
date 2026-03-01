import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_index_returns_200_with_archived_event(page_client, archived_event, archived_compo):
    response = page_client.get(reverse("archive:index"))
    assert response.status_code == 200
    assert "arkisto/index.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_index_empty_state_without_events(page_client):
    response = page_client.get(reverse("archive:index"))
    assert response.status_code == 200
    assert "arkisto/empty.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_index_ignores_non_archived_event(page_client, non_archived_event):
    response = page_client.get(reverse("archive:index"))
    assert response.status_code == 200
    assert "arkisto/empty.html" in [t.name for t in response.templates]
