import pytest

from Instanssi.kompomaatti.models import Entry, Event


def get_reorder_url(event_id):
    return f"/api/v2/admin/event/{event_id}/kompomaatti/entries/reorder/"


@pytest.mark.django_db
def test_reorder_unauthenticated(api_client, event):
    """Test that unauthenticated users cannot reorder entries."""
    url = get_reorder_url(event.id)
    response = api_client.post(url, data={"compo": 1, "entry_ids": []}, format="json")
    assert response.status_code == 401


@pytest.mark.django_db
def test_reorder_unauthorized(auth_client, event):
    """Test that authenticated users without permissions cannot reorder entries."""
    url = get_reorder_url(event.id)
    response = auth_client.post(url, data={"compo": 1, "entry_ids": []}, format="json")
    assert response.status_code == 403


@pytest.mark.django_db
def test_reorder_entries(
    staff_api_client, editable_compo_entry, open_compo, base_user, entry_zip, image_png
):
    """Test successful reordering of entries within a compo."""
    # Create a second entry in the same compo
    entry2 = Entry.objects.create(
        user=base_user,
        compo=open_compo,
        name="Second Entry",
        description="desc",
        creator="creator2",
        entryfile=editable_compo_entry.entryfile,
    )

    url = get_reorder_url(open_compo.event_id)
    response = staff_api_client.post(
        url,
        data={"compo": open_compo.id, "entry_ids": [entry2.id, editable_compo_entry.id]},
        format="json",
    )
    assert response.status_code == 200
    assert response.data["ok"] is True

    # Verify order_index was set correctly
    entry2.refresh_from_db()
    editable_compo_entry.refresh_from_db()
    assert entry2.order_index == 0
    assert editable_compo_entry.order_index == 1


@pytest.mark.django_db
def test_reorder_missing_compo(staff_api_client, event):
    """Test reorder with missing compo field."""
    url = get_reorder_url(event.id)
    response = staff_api_client.post(url, data={"entry_ids": [1]}, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_reorder_missing_entry_ids(staff_api_client, event, open_compo):
    """Test reorder with missing entry_ids field."""
    url = get_reorder_url(event.id)
    response = staff_api_client.post(url, data={"compo": open_compo.id}, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_reorder_wrong_event(staff_api_client, editable_compo_entry, open_compo):
    """Test reorder with compo from a different event."""
    other_event = Event.objects.create(name="Other Event", date="2026-01-01")
    url = get_reorder_url(other_event.id)
    response = staff_api_client.post(
        url,
        data={"compo": open_compo.id, "entry_ids": [editable_compo_entry.id]},
        format="json",
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_reorder_duplicate_entry_ids(staff_api_client, editable_compo_entry, open_compo):
    """Test reorder rejects duplicate entry IDs."""
    url = get_reorder_url(open_compo.event_id)
    response = staff_api_client.post(
        url,
        data={"compo": open_compo.id, "entry_ids": [editable_compo_entry.id, editable_compo_entry.id]},
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_reorder_entry_from_wrong_compo(staff_api_client, votable_compo_entry, open_compo):
    """Test reorder rejects entries that don't belong to the specified compo."""
    url = get_reorder_url(open_compo.event_id)
    response = staff_api_client.post(
        url,
        data={"compo": open_compo.id, "entry_ids": [votable_compo_entry.id]},
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_reorder_partial_entries_rejected(staff_api_client, editable_compo_entry, open_compo, base_user):
    """Test reorder rejects a subset of entries (all compo entries must be included)."""
    Entry.objects.create(
        user=base_user,
        compo=open_compo,
        name="Second Entry",
        description="desc",
        creator="creator2",
        entryfile=editable_compo_entry.entryfile,
    )

    url = get_reorder_url(open_compo.event_id)
    response = staff_api_client.post(
        url,
        data={"compo": open_compo.id, "entry_ids": [editable_compo_entry.id]},
        format="json",
    )
    assert response.status_code == 400
