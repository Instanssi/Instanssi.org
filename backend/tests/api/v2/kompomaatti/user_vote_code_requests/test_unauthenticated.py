import pytest


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/user/kompomaatti/vote_code_requests/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 401),
        ("POST", 401),
        ("PUT", 401),
        ("PATCH", 401),
    ],
)
def test_unauthenticated_list(api_client, event, method, status):
    """Test that unauthenticated requests are rejected."""
    base_url = get_base_url(event.id)
    assert api_client.generic(method, base_url).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 401),
        ("PUT", 401),
        ("PATCH", 401),
    ],
)
def test_unauthenticated_detail(api_client, vote_code_request, method, status):
    """Test that unauthenticated requests to detail endpoints are rejected."""
    base_url = get_base_url(vote_code_request.event_id)
    detail_url = f"{base_url}{vote_code_request.id}/"
    assert api_client.generic(method, detail_url).status_code == status
