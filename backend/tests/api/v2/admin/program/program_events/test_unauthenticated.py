import pytest


def get_base_url(event_id):
    return f"/api/v2/admin/event/{event_id}/program/events/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 401),
        ("POST", 401),
        ("PUT", 401),
        ("PATCH", 401),
        ("DELETE", 401),
    ],
)
def test_unauthenticated_program_events_list(api_client, event, method, status):
    """Test unauthenticated access to list endpoint (Not logged in)."""
    base_url = get_base_url(event.id)
    assert api_client.generic(method, base_url).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 401),
        ("POST", 401),
        ("PUT", 401),
        ("PATCH", 401),
        ("DELETE", 401),
    ],
)
def test_unauthenticated_program_events_detail(api_client, program_event, method, status):
    """Test unauthenticated access to program event detail endpoint (Not logged in)."""
    base_url = get_base_url(program_event.event_id)
    url = f"{base_url}{program_event.id}/"
    assert api_client.generic(method, url).status_code == status
