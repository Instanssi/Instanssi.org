import pytest


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/kompomaatti/competitions/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 200),  # Public read access for active competitions
        ("POST", 401),  # Create denied
        ("PUT", 401),  # Not allowed on list
        ("PATCH", 401),  # Not allowed on list
        ("DELETE", 401),  # Not allowed on list
    ],
)
def test_unauthenticated_competitions_list(api_client, event, method, status):
    """Test unauthenticated access to list endpoint (Not logged in)."""
    base_url = get_base_url(event.id)
    assert api_client.generic(method, base_url).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 404),  # Returns 404 if competition doesn't exist
        ("POST", 401),  # Not allowed on detail
        ("PUT", 401),  # Replace denied
        ("PATCH", 401),  # Update denied
        ("DELETE", 401),  # Delete denied
    ],
)
def test_unauthenticated_competitions_nonexistent_detail(api_client, event, method, status):
    """Test unauthenticated access to non-existent competition detail endpoint (Not logged in)."""
    base_url = get_base_url(event.id)
    url = f"{base_url}999999/"
    assert api_client.generic(method, url).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 200),  # Public read access to existing active competition
        ("POST", 401),  # Not allowed on detail
        ("PUT", 401),  # Replace denied
        ("PATCH", 401),  # Update denied
        ("DELETE", 401),  # Delete denied
    ],
)
def test_unauthenticated_competitions_existing_detail(api_client, event, competition, method, status):
    """Test unauthenticated access to existing competition detail endpoint (Not logged in)."""
    base_url = get_base_url(event.id)
    url = f"{base_url}{competition.id}/"
    assert api_client.generic(method, url).status_code == status


@pytest.mark.django_db
def test_anonymous_can_read_active_competitions(api_client, competition):
    """Test that anonymous users can read active competitions"""
    base_url = get_base_url(competition.event_id)
    # List active competitions
    req = api_client.get(base_url)
    assert req.status_code == 200
    assert len(req.data) >= 1
    # Detail view of active competition
    req = api_client.get(f"{base_url}{competition.id}/")
    assert req.status_code == 200
    assert req.data["id"] == competition.id


@pytest.mark.django_db
def test_anonymous_cannot_see_inactive_competitions(api_client, inactive_competition):
    """Test that anonymous users cannot see inactive competitions"""
    base_url = get_base_url(inactive_competition.event_id)

    # Anonymous users should not see inactive competitions in list
    anon_req = api_client.get(base_url)
    assert anon_req.status_code == 200
    anon_ids = [comp["id"] for comp in anon_req.data]
    assert inactive_competition.id not in anon_ids

    # Anonymous users should get 404 when trying to access inactive competition detail
    detail_req = api_client.get(f"{base_url}{inactive_competition.id}/")
    assert detail_req.status_code == 404
