import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse


@pytest.mark.django_db
def test_entry_index_returns_200(page_client, archived_entry):
    response = page_client.get(reverse("archive:entry", args=[archived_entry.id]))
    assert response.status_code == 200
    assert "arkisto/entry.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_entry_index_404_for_non_archived_event_entry(page_client, non_archived_event, base_user, entry_zip):
    from Instanssi.kompomaatti.models import Compo, Entry

    compo = Compo.objects.create(
        event=non_archived_event,
        name="Non-Archived Compo",
        description="Compo in non-archived event",
        adding_end="2025-01-10T12:00:00Z",
        editing_end="2025-01-11T12:00:00Z",
        compo_start="2025-01-12T12:00:00Z",
        voting_end="2025-01-13T12:00:00Z",
    )
    entry = Entry.objects.create(
        compo=compo,
        user=base_user,
        name="Non-Archived Entry",
        creator="Creator",
        entryfile=entry_zip,
    )
    response = page_client.get(reverse("archive:entry", args=[entry.id]))
    assert response.status_code == 404


@pytest.mark.django_db
def test_entry_index_404_for_hidden_compo_entry(page_client, hidden_compo_entry):
    response = page_client.get(reverse("archive:entry", args=[hidden_compo_entry.id]))
    assert response.status_code == 404


@pytest.mark.django_db
def test_entry_index_404_for_nonexistent(page_client):
    response = page_client.get(reverse("archive:entry", args=[99999]))
    assert response.status_code == 404
