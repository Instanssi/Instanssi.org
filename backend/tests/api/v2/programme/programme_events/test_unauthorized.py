import pytest


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/programme/events/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 200),  # Public read access for active programme events
        ("POST", 403),  # Create denied (authenticated but no permissions)
        ("PUT", 403),  # Not allowed on list
        ("PATCH", 403),  # Not allowed on list
        ("DELETE", 403),  # Not allowed on list
    ],
)
def test_unauthorized_programme_events_list(auth_client, event, method, status):
    """Test unauthorized access to list endpoint (Logged in without permissions).

    The programme events endpoint allows public read access but requires
    ext_programme.add/change/delete_programmeevent permissions for writes.
    """
    base_url = get_base_url(event.id)
    assert auth_client.generic(method, base_url).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 200),  # Public read access to existing active programme event
        ("POST", 403),  # Not allowed on detail
        ("PUT", 403),  # Replace denied
        ("PATCH", 403),  # Update denied
        ("DELETE", 403),  # Delete denied
    ],
)
def test_unauthorized_programme_events_detail(auth_client, programme_event, method, status):
    """Test unauthorized access to existing programme event detail endpoint.

    The programme events endpoint allows public read access but requires
    ext_programme.add/change/delete_programmeevent permissions for writes.
    """
    base_url = get_base_url(programme_event.event_id)
    url = f"{base_url}{programme_event.id}/"
    assert auth_client.generic(method, url).status_code == status


@pytest.mark.django_db
def test_unauthorized_user_cannot_see_inactive_programme_events(auth_client, inactive_programme_event):
    """Test that users without permissions cannot see inactive programme events."""
    base_url = get_base_url(inactive_programme_event.event_id)

    # Users without permissions should not see inactive programme events in list
    req = auth_client.get(base_url)
    assert req.status_code == 200
    ids = [pe["id"] for pe in req.data]
    assert inactive_programme_event.id not in ids

    # Users without permissions should get 404 for inactive programme event detail
    detail_req = auth_client.get(f"{base_url}{inactive_programme_event.id}/")
    assert detail_req.status_code == 404
