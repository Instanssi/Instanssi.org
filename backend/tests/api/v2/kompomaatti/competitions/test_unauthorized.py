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


@pytest.mark.django_db
def test_unauthorized_cannot_see_inactive_competitions(auth_client, inactive_competition):
    """Test that users without permissions cannot see inactive competitions"""
    base_url = get_base_url(inactive_competition.event_id)

    # Unauthorized users should not see inactive competitions in list
    unauth_req = auth_client.get(base_url)
    assert unauth_req.status_code == 200
    unauth_ids = [comp["id"] for comp in unauth_req.data]
    assert inactive_competition.id not in unauth_ids

    # Unauthorized users should get 404 when trying to access inactive competition detail
    detail_req = auth_client.get(f"{base_url}{inactive_competition.id}/")
    assert detail_req.status_code == 404
