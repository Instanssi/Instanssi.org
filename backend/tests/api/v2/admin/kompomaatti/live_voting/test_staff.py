import pytest

from Instanssi.kompomaatti.models import Entry, LiveVotingState


def get_base_url(event_id, compo_id):
    return f"/api/v2/admin/event/{event_id}/kompomaatti/live_voting/{compo_id}/"


@pytest.mark.django_db
def test_get_state_auto_creates(staff_api_client, event, live_voting_compo):
    """GET auto-creates LiveVotingState if it doesn't exist."""
    url = get_base_url(event.id, live_voting_compo.id)
    resp = staff_api_client.get(url)
    assert resp.status_code == 200
    assert resp.data["compo"] == live_voting_compo.id
    assert resp.data["voting_open"] is False
    assert resp.data["current_entry"] is None
    assert LiveVotingState.objects.filter(compo=live_voting_compo).exists()


@pytest.mark.django_db
def test_get_state_with_entries(staff_api_client, event, live_voting_compo, live_voting_entries):
    """GET returns all entries with reveal status."""
    url = get_base_url(event.id, live_voting_compo.id)
    resp = staff_api_client.get(url)
    assert resp.status_code == 200
    assert len(resp.data["entries"]) == 3
    for entry_data in resp.data["entries"]:
        assert entry_data["live_voting_revealed"] is False
        assert set(entry_data.keys()) == {"id", "live_voting_revealed"}


@pytest.mark.django_db
def test_reveal_entry(staff_api_client, event, live_voting_compo, live_voting_entries):
    """POST reveal_entry reveals an entry and sets it as current."""
    url = f"{get_base_url(event.id, live_voting_compo.id)}reveal_entry/"
    entry = live_voting_entries[0]

    resp = staff_api_client.post(url, {"entry_id": entry.id}, format="json")
    assert resp.status_code == 200
    assert resp.data["current_entry"] == entry.id

    entry.refresh_from_db()
    assert entry.live_voting_revealed is True


@pytest.mark.django_db
def test_reveal_already_revealed_entry(staff_api_client, event, live_voting_compo, live_voting_entries):
    """Re-revealing an already revealed entry just updates current_entry."""
    url = f"{get_base_url(event.id, live_voting_compo.id)}reveal_entry/"
    entry = live_voting_entries[0]

    staff_api_client.post(url, {"entry_id": entry.id}, format="json")

    resp = staff_api_client.post(url, {"entry_id": entry.id}, format="json")
    assert resp.status_code == 200
    entry.refresh_from_db()
    assert entry.live_voting_revealed is True


@pytest.mark.django_db
def test_hide_entry(staff_api_client, event, live_voting_compo, live_voting_entries):
    """POST hide_entry hides a revealed entry."""
    reveal_url = f"{get_base_url(event.id, live_voting_compo.id)}reveal_entry/"
    hide_url = f"{get_base_url(event.id, live_voting_compo.id)}hide_entry/"
    entry = live_voting_entries[0]

    staff_api_client.post(reveal_url, {"entry_id": entry.id}, format="json")
    resp = staff_api_client.post(hide_url, {"entry_id": entry.id}, format="json")
    assert resp.status_code == 200

    entry.refresh_from_db()
    assert entry.live_voting_revealed is False


@pytest.mark.django_db
def test_hide_current_entry_clears_current(staff_api_client, event, live_voting_compo, live_voting_entries):
    """Hiding the current entry clears current_entry on the state."""
    base_url = get_base_url(event.id, live_voting_compo.id)
    entry = live_voting_entries[0]

    staff_api_client.post(f"{base_url}reveal_entry/", {"entry_id": entry.id}, format="json")
    resp = staff_api_client.post(f"{base_url}hide_entry/", {"entry_id": entry.id}, format="json")
    assert resp.data["current_entry"] is None


@pytest.mark.django_db
def test_reveal_all(staff_api_client, event, live_voting_compo, live_voting_entries):
    """POST reveal_all reveals all entries."""
    url = f"{get_base_url(event.id, live_voting_compo.id)}reveal_all/"
    resp = staff_api_client.post(url)
    assert resp.status_code == 200

    revealed_count = Entry.objects.filter(compo=live_voting_compo, live_voting_revealed=True).count()
    assert revealed_count == 3


@pytest.mark.django_db
def test_hide_all(staff_api_client, event, live_voting_compo, live_voting_entries):
    """POST hide_all hides all entries and clears current_entry."""
    base_url = get_base_url(event.id, live_voting_compo.id)

    # Reveal all first
    staff_api_client.post(f"{base_url}reveal_all/")

    # Hide all
    resp = staff_api_client.post(f"{base_url}hide_all/")
    assert resp.status_code == 200
    assert resp.data["current_entry"] is None

    revealed_count = Entry.objects.filter(compo=live_voting_compo, live_voting_revealed=True).count()
    assert revealed_count == 0


@pytest.mark.django_db
def test_reset(staff_api_client, event, live_voting_compo, live_voting_entries):
    """POST reset hides all entries, closes voting, clears current_entry."""
    base_url = get_base_url(event.id, live_voting_compo.id)

    # Reveal all and open voting
    staff_api_client.post(f"{base_url}reveal_all/")
    staff_api_client.patch(base_url, {"voting_open": True}, format="json")

    # Reset
    resp = staff_api_client.post(f"{base_url}reset/")
    assert resp.status_code == 200
    assert resp.data["voting_open"] is False
    assert resp.data["current_entry"] is None

    revealed_count = Entry.objects.filter(compo=live_voting_compo, live_voting_revealed=True).count()
    assert revealed_count == 0


@pytest.mark.django_db
def test_update_voting_open(staff_api_client, event, live_voting_compo):
    """PATCH can toggle voting_open."""
    url = get_base_url(event.id, live_voting_compo.id)

    resp = staff_api_client.patch(url, {"voting_open": True}, format="json")
    assert resp.status_code == 200
    assert resp.data["voting_open"] is True

    resp = staff_api_client.patch(url, {"voting_open": False}, format="json")
    assert resp.status_code == 200
    assert resp.data["voting_open"] is False


@pytest.mark.django_db
def test_update_current_entry(staff_api_client, event, live_voting_compo, live_voting_entries):
    """PATCH can set current_entry."""
    url = get_base_url(event.id, live_voting_compo.id)
    entry = live_voting_entries[0]

    resp = staff_api_client.patch(url, {"current_entry": entry.id}, format="json")
    assert resp.status_code == 200
    assert resp.data["current_entry"] == entry.id

    resp = staff_api_client.patch(url, {"current_entry": None}, format="json")
    assert resp.status_code == 200
    assert resp.data["current_entry"] is None


@pytest.mark.django_db
def test_reveal_entry_wrong_compo(staff_api_client, event, live_voting_compo, votable_compo_entry):
    """Revealing an entry from a different compo returns 404."""
    url = f"{get_base_url(event.id, live_voting_compo.id)}reveal_entry/"
    resp = staff_api_client.post(url, {"entry_id": votable_compo_entry.id}, format="json")
    assert resp.status_code == 404


@pytest.mark.django_db
def test_update_current_entry_wrong_compo(staff_api_client, event, live_voting_compo, votable_compo_entry):
    """Setting current_entry to an entry from a different compo returns 404."""
    url = get_base_url(event.id, live_voting_compo.id)
    resp = staff_api_client.patch(url, {"current_entry": votable_compo_entry.id}, format="json")
    assert resp.status_code == 404


@pytest.mark.django_db
def test_reveal_out_of_order_rejected(staff_api_client, event, live_voting_compo, live_voting_entries):
    """Revealing an entry that is not the next in order_index order returns 400."""
    url = f"{get_base_url(event.id, live_voting_compo.id)}reveal_entry/"
    # Try to reveal the second entry without revealing the first
    resp = staff_api_client.post(url, {"entry_id": live_voting_entries[1].id}, format="json")
    assert resp.status_code == 400


@pytest.mark.django_db
def test_hide_not_last_revealed_rejected(staff_api_client, event, live_voting_compo, live_voting_entries):
    """Hiding an entry that is not the last revealed returns 400."""
    base_url = get_base_url(event.id, live_voting_compo.id)
    reveal_url = f"{base_url}reveal_entry/"
    hide_url = f"{base_url}hide_entry/"

    # Reveal first two entries
    staff_api_client.post(reveal_url, {"entry_id": live_voting_entries[0].id}, format="json")
    staff_api_client.post(reveal_url, {"entry_id": live_voting_entries[1].id}, format="json")

    # Try to hide the first (not the last revealed)
    resp = staff_api_client.post(hide_url, {"entry_id": live_voting_entries[0].id}, format="json")
    assert resp.status_code == 400

    # Hiding the last revealed should work
    resp = staff_api_client.post(hide_url, {"entry_id": live_voting_entries[1].id}, format="json")
    assert resp.status_code == 200
