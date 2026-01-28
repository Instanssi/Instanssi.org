import pytest


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/user/kompomaatti/ticket_vote_codes/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 401),
        ("POST", 401),
    ],
)
def test_unauthenticated_ticket_vote_codes_list(api_client, event, method, status):
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
def test_unauthenticated_ticket_vote_codes_detail(api_client, ticket_vote_code, method, status):
    """Test that unauthenticated requests to detail endpoints are rejected."""
    base_url = get_base_url(ticket_vote_code.event_id)
    detail_url = f"{base_url}{ticket_vote_code.id}/"
    assert api_client.generic(method, detail_url).status_code == status
