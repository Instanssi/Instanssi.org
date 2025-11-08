import pytest


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/kompomaatti/ticket_vote_codes/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "obj,method,status",
    [
        (False, "GET", 403),
        (True, "GET", 403),
        (False, "POST", 403),
        (True, "DELETE", 403),
        (True, "PATCH", 403),
        (True, "PUT", 403),
    ],
)
def test_unauthorized_ticket_vote_codes(auth_client, event, obj, method, status):
    """Test unauthorized access (Logged in, but no permissions)"""
    base_url = get_base_url(event.id)
    url = f"{base_url}1/" if obj else base_url
    assert auth_client.generic(method, url).status_code == status
