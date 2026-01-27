import pytest


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/user/kompomaatti/votes/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 401),
        ("POST", 401),
    ],
)
def test_unauthenticated_votes_list(api_client, event, method, status):
    """Test that unauthenticated requests are rejected."""
    base_url = get_base_url(event.id)
    assert api_client.generic(method, base_url).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 401),
    ],
)
def test_unauthenticated_votes_detail(api_client, entry_vote_group, method, status):
    """Test that unauthenticated requests to detail endpoints are rejected."""
    base_url = get_base_url(entry_vote_group.compo.event_id)
    detail_url = f"{base_url}{entry_vote_group.id}/"
    assert api_client.generic(method, detail_url).status_code == status
