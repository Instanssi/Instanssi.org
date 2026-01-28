import pytest


def get_base_url(event_id):
    return f"/api/v2/admin/event/{event_id}/arkisto/videos/"


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
def test_unauthorized_videos_list(auth_client, archived_event, method, status):
    """Test unauthorized access to list endpoint (Logged in without permissions)."""
    base_url = get_base_url(archived_event.id)
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
def test_unauthorized_videos_detail(auth_client, other_video, method, status):
    """Test unauthorized access to video detail endpoint (Logged in without permissions)."""
    base_url = get_base_url(other_video.category.event_id)
    url = f"{base_url}{other_video.id}/"
    assert auth_client.generic(method, url).status_code == status
