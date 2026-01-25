import pytest


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/kompomaatti/entries/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "obj,method,status",
    [
        (False, "GET", 200),  # Public can read list when voting started
        (True, "GET", 200),  # Public can read detail when voting started
        (False, "POST", 401),
        (True, "DELETE", 401),
        (True, "PATCH", 401),
        (True, "PUT", 401),
    ],
)
def test_unauthenticated_compo_entries(api_client, event, votable_compo_entry, obj, method, status):
    """Test unauthenticated access (Not logged in). GET is allowed after voting starts."""
    base_url = get_base_url(event.id)
    url = f"{base_url}{votable_compo_entry.id}/" if obj else base_url
    assert api_client.generic(method, url).status_code == status


@pytest.mark.django_db
def test_unauthenticated_cannot_see_non_votable_entries(api_client, editable_compo_entry):
    """Test that unauthenticated users cannot see entries before voting has started"""
    base_url = get_base_url(editable_compo_entry.compo.event_id)

    # Entry should not appear in list view
    list_req = api_client.get(base_url)
    assert list_req.status_code == 200
    entry_ids = [e["id"] for e in list_req.data]
    assert editable_compo_entry.id not in entry_ids

    # Detail view should return 404
    detail_req = api_client.get(f"{base_url}{editable_compo_entry.id}/")
    assert detail_req.status_code == 404


@pytest.mark.django_db
def test_unauthenticated_can_see_votable_entries(api_client, votable_compo_entry):
    """Test that unauthenticated users can see entries when voting has started"""
    base_url = get_base_url(votable_compo_entry.compo.event_id)

    # Entry should appear in list view
    list_req = api_client.get(base_url)
    assert list_req.status_code == 200
    entry_ids = [e["id"] for e in list_req.data]
    assert votable_compo_entry.id in entry_ids

    # Detail view should return 200
    detail_req = api_client.get(f"{base_url}{votable_compo_entry.id}/")
    assert detail_req.status_code == 200


@pytest.mark.django_db
def test_public_cannot_see_score_rank_before_results_shown(api_client, votable_compo_entry):
    """Test that public users cannot see score/rank before show_voting_results is enabled"""
    votable_compo_entry.compo.show_voting_results = False
    votable_compo_entry.compo.save()

    base_url = get_base_url(votable_compo_entry.compo.event_id)
    req = api_client.get(f"{base_url}{votable_compo_entry.id}/")
    assert req.status_code == 200
    assert req.data["score"] is None
    assert req.data["rank"] is None


@pytest.mark.django_db
def test_public_can_see_score_rank_after_results_shown(api_client, votable_compo_entry):
    """Test that public users can see score/rank when show_voting_results is enabled"""
    votable_compo_entry.compo.show_voting_results = True
    votable_compo_entry.compo.save()

    base_url = get_base_url(votable_compo_entry.compo.event_id)
    req = api_client.get(f"{base_url}{votable_compo_entry.id}/")
    assert req.status_code == 200
    assert req.data["score"] is not None
    assert req.data["rank"] is not None


@pytest.mark.django_db
def test_public_can_see_alternate_files(api_client, votable_alternate_entry_file):
    """Test that public users can see alternate_files when voting has started"""
    entry = votable_alternate_entry_file.entry
    base_url = get_base_url(entry.compo.event_id)
    req = api_client.get(f"{base_url}{entry.id}/")
    assert req.status_code == 200
    assert "alternate_files" in req.data
    assert len(req.data["alternate_files"]) == 1
    alt_file = req.data["alternate_files"][0]
    assert alt_file["format"] == "audio/webm;codecs=opus"
    assert "url" in alt_file
