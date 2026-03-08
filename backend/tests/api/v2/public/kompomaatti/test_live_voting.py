import pytest

from Instanssi.kompomaatti.models import Entry, LiveVotingState


def get_url(event_id, compo_id):
    return f"/api/v2/public/event/{event_id}/kompomaatti/live_voting/{compo_id}/"


@pytest.mark.django_db
def test_public_live_voting_state(
    api_client, event, live_voting_compo, live_voting_state, live_voting_entries
):
    """Public endpoint returns live voting state with revealed entries."""
    # Reveal first entry
    entry = live_voting_entries[0]
    Entry.objects.filter(pk=entry.pk).update(live_voting_revealed=True)
    live_voting_state.voting_open = True
    live_voting_state.current_entry = entry
    live_voting_state.save()

    url = get_url(event.id, live_voting_compo.id)
    resp = api_client.get(url)
    assert resp.status_code == 200
    assert resp.data["compo"] == live_voting_compo.id
    assert resp.data["voting_open"] is True
    assert resp.data["current_entry"] == entry.id
    assert resp.data["revealed_entries"] == [entry.id]
    assert "Last-Modified" in resp


@pytest.mark.django_db
def test_public_live_voting_404_non_live(api_client, event, open_compo):
    """Returns 404 for compos without live voting enabled."""
    url = get_url(event.id, open_compo.id)
    resp = api_client.get(url)
    assert resp.status_code == 404


@pytest.mark.django_db
def test_public_live_voting_404_no_state(api_client, event, live_voting_compo):
    """Returns 404 when no LiveVotingState exists."""
    url = get_url(event.id, live_voting_compo.id)
    resp = api_client.get(url)
    assert resp.status_code == 404


@pytest.mark.django_db
def test_public_live_voting_304_not_modified(api_client, event, live_voting_compo, live_voting_state):
    """Returns 304 when state hasn't changed since If-Modified-Since."""
    url = get_url(event.id, live_voting_compo.id)

    # Get the state first
    resp = api_client.get(url)
    assert resp.status_code == 200
    last_modified = resp["Last-Modified"]

    # Request with If-Modified-Since
    resp = api_client.get(url, HTTP_IF_MODIFIED_SINCE=last_modified)
    assert resp.status_code == 304


@pytest.mark.django_db
def test_public_live_voting_hidden_event(api_client, live_voting_compo, live_voting_state):
    """Returns 404 for hidden events."""
    event = live_voting_compo.event
    event.hidden = True
    event.save()

    url = get_url(event.id, live_voting_compo.id)
    resp = api_client.get(url)
    assert resp.status_code == 404


@pytest.mark.django_db
def test_public_live_voting_inactive_compo(api_client, event, live_voting_compo, live_voting_state):
    """Returns 404 for inactive compos."""
    live_voting_compo.active = False
    live_voting_compo.save()

    url = get_url(event.id, live_voting_compo.id)
    resp = api_client.get(url)
    assert resp.status_code == 404
