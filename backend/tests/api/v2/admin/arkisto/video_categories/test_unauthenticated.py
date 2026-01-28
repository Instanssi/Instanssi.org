import pytest


def get_base_url(event_id):
    return f"/api/v2/admin/event/{event_id}/arkisto/video_categories/"


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
def test_unauthenticated_video_categories_list(api_client, archived_event, method, status):
    """Test unauthenticated access to list endpoint (Not logged in)."""
    base_url = get_base_url(archived_event.id)
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
def test_unauthenticated_video_categories_detail(api_client, video_category, method, status):
    """Test unauthenticated access to video category detail endpoint (Not logged in)."""
    base_url = get_base_url(video_category.event_id)
    url = f"{base_url}{video_category.id}/"
    assert api_client.generic(method, url).status_code == status
