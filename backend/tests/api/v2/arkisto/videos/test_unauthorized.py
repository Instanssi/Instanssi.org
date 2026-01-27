import pytest


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/archive/videos/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 200),  # Public read access for archived events
        ("POST", 403),  # Create denied (authenticated but no permissions)
        ("PUT", 403),  # Not allowed on list
        ("PATCH", 403),  # Not allowed on list
        ("DELETE", 403),  # Not allowed on list
    ],
)
def test_unauthorized_videos_list(auth_client, archived_event, method, status):
    """Test unauthorized access to list endpoint (Logged in without permissions).

    The videos endpoint allows public read access for archived events
    but requires arkisto.add/change/delete_othervideo permissions for writes.
    """
    base_url = get_base_url(archived_event.id)
    assert auth_client.generic(method, base_url).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 200),  # Public read access to existing video
        ("POST", 403),  # Not allowed on detail
        ("PUT", 403),  # Replace denied
        ("PATCH", 403),  # Update denied
        ("DELETE", 403),  # Delete denied
    ],
)
def test_unauthorized_videos_detail(auth_client, other_video, method, status):
    """Test unauthorized access to existing video detail endpoint.

    The videos endpoint allows public read access for archived events
    but requires arkisto.add/change/delete_othervideo permissions for writes.
    """
    base_url = get_base_url(other_video.category.event_id)
    url = f"{base_url}{other_video.id}/"
    assert auth_client.generic(method, url).status_code == status


@pytest.mark.django_db
def test_unauthorized_user_cannot_see_videos_for_non_archived_events(auth_client, other_video_non_archived):
    """Test that users without permissions cannot see videos for non-archived events."""
    base_url = get_base_url(other_video_non_archived.category.event_id)

    # Users without permissions should not see videos for non-archived events
    req = auth_client.get(base_url)
    assert req.status_code == 200
    ids = [v["id"] for v in req.data]
    assert other_video_non_archived.id not in ids

    # Users without permissions should get 404 for non-archived video detail
    detail_req = auth_client.get(f"{base_url}{other_video_non_archived.id}/")
    assert detail_req.status_code == 404
