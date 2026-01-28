import pytest


def get_base_url(event_id):
    return f"/api/v2/admin/event/{event_id}/arkisto/video_categories/"


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
def test_unauthorized_video_categories_list(auth_client, archived_event, method, status):
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
def test_unauthorized_video_categories_detail(auth_client, video_category, method, status):
    """Test unauthorized access to video category detail endpoint (Logged in without permissions)."""
    base_url = get_base_url(video_category.event_id)
    url = f"{base_url}{video_category.id}/"
    assert auth_client.generic(method, url).status_code == status
