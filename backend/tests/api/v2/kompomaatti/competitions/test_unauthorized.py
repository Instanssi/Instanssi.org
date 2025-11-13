import pytest


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/kompomaatti/competitions/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 200),  # Public read access for active competitions
        ("POST", 403),  # Create denied
        ("PUT", 403),  # Not allowed on list
        ("PATCH", 403),  # Not allowed on list
        ("DELETE", 403),  # Not allowed on list
    ],
)
def test_unauthorized_competitions_list(auth_client, event, method, status):
    """Test unauthorized access to list endpoint (Logged in, but no permissions)."""
    base_url = get_base_url(event.id)
    assert auth_client.generic(method, base_url).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 404),  # Returns 404 if competition doesn't exist
        ("POST", 403),  # Not allowed on detail
        ("PUT", 403),  # Replace denied
        ("PATCH", 403),  # Update denied
        ("DELETE", 403),  # Delete denied
    ],
)
def test_unauthorized_competitions_nonexistent_detail(auth_client, event, method, status):
    """Test unauthorized access to non-existent competition detail endpoint (Logged in, but no permissions)."""
    base_url = get_base_url(event.id)
    url = f"{base_url}999999/"
    assert auth_client.generic(method, url).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 200),  # Public read access to existing active competition
        ("POST", 403),  # Not allowed on detail
        ("PUT", 403),  # Replace denied
        ("PATCH", 403),  # Update denied
        ("DELETE", 403),  # Delete denied
    ],
)
def test_unauthorized_competitions_existing_detail(auth_client, event, competition, method, status):
    """Test unauthorized access to existing competition detail endpoint (Logged in, but no permissions)."""
    base_url = get_base_url(event.id)
    url = f"{base_url}{competition.id}/"
    assert auth_client.generic(method, url).status_code == status


@pytest.mark.django_db
def test_unauthorized_can_read_active_competitions(auth_client, competition):
    """Test that users without permissions can read active competitions"""
    base_url = get_base_url(competition.event_id)
    # List active competitions
    req = auth_client.get(base_url)
    assert req.status_code == 200
    assert len(req.data) >= 1
    # Detail view of active competition
    req = auth_client.get(f"{base_url}{competition.id}/")
    assert req.status_code == 200
    assert req.data["id"] == competition.id
