import pytest


def get_base_url(event_id):
    return f"/api/v2/admin/event/{event_id}/arkisto/archiver/"


@pytest.mark.django_db
def test_unauthorized_status_endpoint(auth_client, past_event):
    """Test that authenticated users without permissions can still get status."""
    # Status endpoint only requires IsAuthenticated, not specific permissions
    url = get_base_url(past_event.id) + "status/"
    assert auth_client.get(url).status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize(
    "endpoint,method,status",
    [
        ("show/", "POST", 403),
        ("hide/", "POST", 403),
        ("optimize-scores/", "POST", 403),
        ("remove-old-votes/", "POST", 403),
        ("transfer-rights/", "POST", 403),
    ],
)
def test_unauthorized_archiver_action_endpoints(auth_client, past_event, endpoint, method, status):
    """Test unauthorized access to archiver action endpoints (Logged in without permissions)."""
    url = get_base_url(past_event.id) + endpoint
    assert auth_client.generic(method, url).status_code == status
