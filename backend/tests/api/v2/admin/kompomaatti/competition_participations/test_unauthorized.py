import pytest


def get_base_url(event_id):
    return f"/api/v2/admin/event/{event_id}/kompomaatti/competition_participations/"


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
def test_unauthorized_competition_participations_list(auth_client, event, method, status):
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
def test_unauthorized_competition_participations_detail(
    auth_client, event, started_competition_participation, method, status
):
    """Test unauthorized access to participation detail endpoint (Logged in, but no permissions)."""
    base_url = get_base_url(event.id)
    url = f"{base_url}{started_competition_participation.id}/"
    assert auth_client.generic(method, url).status_code == status
