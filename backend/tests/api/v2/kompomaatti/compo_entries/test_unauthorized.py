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
