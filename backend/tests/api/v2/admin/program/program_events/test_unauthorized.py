import pytest


def get_base_url(event_id):
    return f"/api/v2/admin/event/{event_id}/program/events/"


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
def test_unauthorized_program_events_list(auth_client, event, method, status):
    """Test unauthorized access to list endpoint (Logged in without permissions)."""
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
def test_unauthorized_program_events_detail(auth_client, program_event, method, status):
    """Test unauthorized access to program event detail endpoint (Logged in without permissions)."""
    base_url = get_base_url(program_event.event_id)
    url = f"{base_url}{program_event.id}/"
    assert auth_client.generic(method, url).status_code == status
