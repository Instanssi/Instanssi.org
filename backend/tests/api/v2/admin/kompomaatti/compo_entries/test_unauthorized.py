import pytest


def get_base_url(event_id):
    return f"/api/v2/admin/event/{event_id}/kompomaatti/entries/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 403),
        ("POST", 403),
        ("PUT", 403),
        ("PATCH", 403),
        ("DELETE", 403),
    ],
)
def test_unauthorized_compo_entries_list(auth_client, event, method, status):
    """Test unauthorized access to list endpoint (Logged in, but no permissions)."""
    base_url = get_base_url(event.id)
    assert auth_client.generic(method, base_url).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 403),
        ("POST", 403),
        ("PUT", 403),
        ("PATCH", 403),
        ("DELETE", 403),
    ],
)
def test_unauthorized_compo_entries_detail(auth_client, event, votable_compo_entry, method, status):
    """Test unauthorized access to entry detail endpoint (Logged in, but no permissions)."""
    base_url = get_base_url(event.id)
    url = f"{base_url}{votable_compo_entry.id}/"
    assert auth_client.generic(method, url).status_code == status
