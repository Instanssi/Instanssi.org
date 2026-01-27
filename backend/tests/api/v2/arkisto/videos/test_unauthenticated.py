import pytest


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/archive/videos/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 200),  # Public read access for archived events
        ("POST", 401),  # Create denied
        ("PUT", 401),  # Not allowed on list
        ("PATCH", 401),  # Not allowed on list
        ("DELETE", 401),  # Not allowed on list
    ],
)
def test_unauthenticated_videos_list(api_client, archived_event, method, status):
    """Test unauthenticated access to list endpoint (Not logged in)."""
    base_url = get_base_url(archived_event.id)
    assert api_client.generic(method, base_url).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 404),  # Returns 404 if video doesn't exist
        ("POST", 401),  # Not allowed on detail
        ("PUT", 401),  # Replace denied
        ("PATCH", 401),  # Update denied
        ("DELETE", 401),  # Delete denied
    ],
)
def test_unauthenticated_videos_nonexistent_detail(api_client, archived_event, method, status):
    """Test unauthenticated access to non-existent video detail endpoint."""
    base_url = get_base_url(archived_event.id)
    url = f"{base_url}999999/"
    assert api_client.generic(method, url).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 200),  # Public read access to existing video
        ("POST", 401),  # Not allowed on detail
        ("PUT", 401),  # Replace denied
        ("PATCH", 401),  # Update denied
        ("DELETE", 401),  # Delete denied
    ],
)
def test_unauthenticated_videos_existing_detail(api_client, other_video, method, status):
    """Test unauthenticated access to existing video detail endpoint."""
    base_url = get_base_url(other_video.category.event_id)
    url = f"{base_url}{other_video.id}/"
    assert api_client.generic(method, url).status_code == status


@pytest.mark.django_db
def test_anonymous_can_read_videos_for_archived_events(api_client, other_video):
    """Test that anonymous users can read videos for archived events."""
    base_url = get_base_url(other_video.category.event_id)
    # List videos
    req = api_client.get(base_url)
    assert req.status_code == 200
    assert len(req.data) >= 1
    # Detail view
    req = api_client.get(f"{base_url}{other_video.id}/")
    assert req.status_code == 200
    assert req.data["id"] == other_video.id
    assert req.data["youtube_url"] is not None
    assert req.data["youtube_url"]["video_id"] == "dQw4w9WgXcQ"


@pytest.mark.django_db
def test_anonymous_cannot_see_videos_for_non_archived_events(api_client, other_video_non_archived):
    """Test that anonymous users cannot see videos for non-archived events."""
    base_url = get_base_url(other_video_non_archived.category.event_id)

    # Anonymous users should not see videos for non-archived events in list
    anon_req = api_client.get(base_url)
    assert anon_req.status_code == 200
    anon_ids = [v["id"] for v in anon_req.data]
    assert other_video_non_archived.id not in anon_ids

    # Anonymous users should get 404 when trying to access non-archived video detail
    detail_req = api_client.get(f"{base_url}{other_video_non_archived.id}/")
    assert detail_req.status_code == 404
