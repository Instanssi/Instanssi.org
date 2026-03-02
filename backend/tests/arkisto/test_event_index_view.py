import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_event_index_returns_200(page_client, archived_event, archived_compo):
    response = page_client.get(reverse("archive:event", args=[archived_event.id]))
    assert response.status_code == 200


@pytest.mark.django_db
def test_event_index_shows_compos(page_client, archived_event, archived_compo, archived_entry):
    response = page_client.get(reverse("archive:event", args=[archived_event.id]))
    assert response.status_code == 200
    assert b"Archived Compo" in response.content


@pytest.mark.django_db
def test_event_index_shows_videos(page_client, archived_event, other_video):
    response = page_client.get(reverse("archive:event", args=[archived_event.id]))
    assert response.status_code == 200
    assert b"Test Video" in response.content


@pytest.mark.django_db
def test_event_index_shows_competitions(
    page_client, archived_event, archived_competition, archived_participation
):
    response = page_client.get(reverse("archive:event", args=[archived_event.id]))
    assert response.status_code == 200
    assert b"Archived Competition" in response.content


@pytest.mark.django_db
def test_event_index_excludes_hidden_compo(page_client, archived_event, hidden_from_archive_compo):
    response = page_client.get(reverse("archive:event", args=[archived_event.id]))
    assert response.status_code == 200
    assert b"Hidden Compo" not in response.content


@pytest.mark.django_db
def test_event_index_excludes_inactive_compo(page_client, archived_event, inactive_archived_compo):
    response = page_client.get(reverse("archive:event", args=[archived_event.id]))
    assert response.status_code == 200
    assert b"Inactive Compo" not in response.content


@pytest.mark.django_db
def test_event_index_404_for_non_archived(page_client, non_archived_event):
    response = page_client.get(reverse("archive:event", args=[non_archived_event.id]))
    assert response.status_code == 404


@pytest.mark.django_db
def test_event_index_404_for_nonexistent(page_client):
    response = page_client.get(reverse("archive:event", args=[99999]))
    assert response.status_code == 404


@pytest.mark.django_db
def test_templates_use_base_theme(page_client, archived_event, archived_compo):
    response = page_client.get(reverse("archive:event", args=[archived_event.id]))
    template_names = [t.name for t in response.templates]
    assert "base_theme/base.html" in template_names
    assert "base_theme/includes/navbar.html" in template_names
