import pytest


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/kompomaatti/ticket_vote_codes/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "obj,method,status",
    [
        (False, "GET", 401),
        (True, "GET", 401),
        (False, "POST", 401),
        (True, "DELETE", 401),
        (True, "PATCH", 401),
        (True, "PUT", 401),
    ],
)
def test_unauthenticated_ticket_vote_codes(api_client, event, obj, method, status):
    """Test unauthenticated access (Not logged in)"""
    base_url = get_base_url(event.id)
    url = f"{base_url}1/" if obj else base_url
    assert api_client.generic(method, url).status_code == status
