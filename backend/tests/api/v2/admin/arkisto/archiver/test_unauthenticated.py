import pytest


def get_base_url(event_id):
    return f"/api/v2/admin/event/{event_id}/arkisto/archiver/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "endpoint,method,status",
    [
        ("status/", "GET", 401),
        ("show/", "POST", 401),
        ("hide/", "POST", 401),
        ("optimize-scores/", "POST", 401),
        ("remove-old-votes/", "POST", 401),
        ("transfer-rights/", "POST", 401),
    ],
)
def test_unauthenticated_archiver_endpoints(api_client, past_event, endpoint, method, status):
    """Test unauthenticated access to archiver endpoints (Not logged in)."""
    url = get_base_url(past_event.id) + endpoint
    assert api_client.generic(method, url).status_code == status
