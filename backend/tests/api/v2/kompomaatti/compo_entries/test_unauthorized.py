import pytest


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/kompomaatti/entries/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "obj,method,status",
    [
        (False, "GET", 200),  # Public can read list when voting started
        (True, "GET", 200),  # Public can read detail when voting started
        (False, "POST", 403),
        (True, "DELETE", 403),
        (True, "PATCH", 403),
        (True, "PUT", 403),
    ],
)
def test_unauthorized_compo_entries(auth_client, event, votable_compo_entry, obj, method, status):
    """Test unauthorized access (Logged in, but no permissions). GET is allowed after voting starts."""
    base_url = get_base_url(event.id)
    url = f"{base_url}{votable_compo_entry.id}/" if obj else base_url
    assert auth_client.generic(method, url).status_code == status


@pytest.mark.django_db
def test_unauthorized_cannot_see_non_votable_entries(auth_client, editable_compo_entry):
    """Test that unauthorized users cannot see entries before voting has started"""
    base_url = get_base_url(editable_compo_entry.compo.event_id)

    # Entry should not appear in list view
    list_req = auth_client.get(base_url)
    assert list_req.status_code == 200
    entry_ids = [e["id"] for e in list_req.data]
    assert editable_compo_entry.id not in entry_ids

    # Detail view should return 404
    detail_req = auth_client.get(f"{base_url}{editable_compo_entry.id}/")
    assert detail_req.status_code == 404


@pytest.mark.django_db
def test_unauthorized_can_see_votable_entries(auth_client, votable_compo_entry):
    """Test that unauthorized users can see entries when voting has started"""
    base_url = get_base_url(votable_compo_entry.compo.event_id)

    # Entry should appear in list view
    list_req = auth_client.get(base_url)
    assert list_req.status_code == 200
    entry_ids = [e["id"] for e in list_req.data]
    assert votable_compo_entry.id in entry_ids

    # Detail view should return 200
    detail_req = auth_client.get(f"{base_url}{votable_compo_entry.id}/")
    assert detail_req.status_code == 200


@pytest.mark.django_db
def test_unauthorized_cannot_see_score_rank_before_results_shown(auth_client, votable_compo_entry):
    """Test that unauthorized users cannot see score/rank before show_voting_results is enabled"""
    votable_compo_entry.compo.show_voting_results = False
    votable_compo_entry.compo.save()

    base_url = get_base_url(votable_compo_entry.compo.event_id)
    req = auth_client.get(f"{base_url}{votable_compo_entry.id}/")
    assert req.status_code == 200
    assert req.data["score"] is None
    assert req.data["rank"] is None


@pytest.mark.django_db
def test_unauthorized_can_see_score_rank_after_results_shown(auth_client, votable_compo_entry):
    """Test that unauthorized users can see score/rank when show_voting_results is enabled"""
    votable_compo_entry.compo.show_voting_results = True
    votable_compo_entry.compo.save()

    base_url = get_base_url(votable_compo_entry.compo.event_id)
    req = auth_client.get(f"{base_url}{votable_compo_entry.id}/")
    assert req.status_code == 200
    assert req.data["score"] is not None
    assert req.data["rank"] is not None
