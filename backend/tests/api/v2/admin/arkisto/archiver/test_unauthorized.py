import pytest


def get_base_url(event_id):
    return f"/api/v2/admin/event/{event_id}/arkisto/archiver/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "endpoint,method",
    [
        ("status/", "GET"),
        ("show/", "POST"),
        ("hide/", "POST"),
        ("optimize-scores/", "POST"),
        ("remove-old-votes/", "POST"),
        ("transfer-rights/", "POST"),
    ],
)
def test_unauthorized_archiver_endpoints(auth_client, past_event, endpoint, method):
    """Test that non-staff users are denied access to all archiver endpoints."""
    url = get_base_url(past_event.id) + endpoint
    assert auth_client.generic(method, url).status_code == 403
