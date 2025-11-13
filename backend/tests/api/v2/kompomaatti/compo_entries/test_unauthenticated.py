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
