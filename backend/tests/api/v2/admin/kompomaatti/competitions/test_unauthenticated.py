import pytest


def get_base_url(event_id):
    return f"/api/v2/admin/event/{event_id}/kompomaatti/competitions/"


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
def test_unauthenticated_competitions_list(api_client, event, method, status):
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
def test_unauthenticated_competitions_detail(api_client, event, competition, method, status):
    """Test unauthenticated access to competition detail endpoint (Not logged in)."""
    base_url = get_base_url(event.id)
    url = f"{base_url}{competition.id}/"
    assert api_client.generic(method, url).status_code == status
