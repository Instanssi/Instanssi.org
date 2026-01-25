import pytest


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/programme/events/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 200),  # Public read access for active programme events
        ("POST", 401),  # Create denied
        ("PUT", 401),  # Not allowed on list
        ("PATCH", 401),  # Not allowed on list
        ("DELETE", 401),  # Not allowed on list
    ],
)
def test_unauthenticated_programme_events_list(api_client, event, method, status):
    """Test unauthenticated access to list endpoint (Not logged in)."""
    base_url = get_base_url(event.id)
    assert api_client.generic(method, base_url).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 404),  # Returns 404 if programme event doesn't exist
        ("POST", 401),  # Not allowed on detail
        ("PUT", 401),  # Replace denied
        ("PATCH", 401),  # Update denied
        ("DELETE", 401),  # Delete denied
    ],
)
def test_unauthenticated_programme_events_nonexistent_detail(api_client, event, method, status):
    """Test unauthenticated access to non-existent programme event detail endpoint."""
    base_url = get_base_url(event.id)
    url = f"{base_url}999999/"
    assert api_client.generic(method, url).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 200),  # Public read access to existing active programme event
        ("POST", 401),  # Not allowed on detail
        ("PUT", 401),  # Replace denied
        ("PATCH", 401),  # Update denied
        ("DELETE", 401),  # Delete denied
    ],
)
def test_unauthenticated_programme_events_existing_detail(api_client, programme_event, method, status):
    """Test unauthenticated access to existing programme event detail endpoint."""
    base_url = get_base_url(programme_event.event_id)
    url = f"{base_url}{programme_event.id}/"
    assert api_client.generic(method, url).status_code == status


@pytest.mark.django_db
def test_anonymous_can_read_active_programme_events(api_client, programme_event):
    """Test that anonymous users can read active programme events."""
    base_url = get_base_url(programme_event.event_id)
    # List active programme events
    req = api_client.get(base_url)
    assert req.status_code == 200
    assert len(req.data) >= 1
    # Detail view of active programme event
    req = api_client.get(f"{base_url}{programme_event.id}/")
    assert req.status_code == 200
    assert req.data["id"] == programme_event.id


@pytest.mark.django_db
def test_anonymous_cannot_see_inactive_programme_events(api_client, inactive_programme_event):
    """Test that anonymous users cannot see inactive programme events."""
    base_url = get_base_url(inactive_programme_event.event_id)

    # Anonymous users should not see inactive programme events in list
    anon_req = api_client.get(base_url)
    assert anon_req.status_code == 200
    anon_ids = [pe["id"] for pe in anon_req.data]
    assert inactive_programme_event.id not in anon_ids

    # Anonymous users should get 404 when trying to access inactive programme event detail
    detail_req = api_client.get(f"{base_url}{inactive_programme_event.id}/")
    assert detail_req.status_code == 404
