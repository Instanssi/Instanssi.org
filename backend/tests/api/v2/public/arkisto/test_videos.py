import pytest


def get_base_url(event_id):
    return f"/api/v2/public/event/{event_id}/archive/videos/"


@pytest.mark.django_db
def test_anonymous_can_list_videos_for_archived_events(api_client, other_video):
    """Test that anonymous users can list videos for archived events."""
    base_url = get_base_url(other_video.category.event_id)
    req = api_client.get(base_url)
    assert req.status_code == 200
    ids = [v["id"] for v in req.data]
    assert other_video.id in ids


@pytest.mark.django_db
def test_anonymous_can_get_video_detail(api_client, other_video):
    """Test that anonymous users can get video details."""
    base_url = get_base_url(other_video.category.event_id)
    req = api_client.get(f"{base_url}{other_video.id}/")
    assert req.status_code == 200
    assert req.data["id"] == other_video.id
    assert req.data["youtube_url"] == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


@pytest.mark.django_db
def test_anonymous_cannot_see_videos_for_non_archived_events(api_client, other_video_non_archived):
    """Test that videos for non-archived events are not visible."""
    base_url = get_base_url(other_video_non_archived.category.event_id)

    # Not in list
    req = api_client.get(base_url)
    assert req.status_code == 200
    ids = [v["id"] for v in req.data]
    assert other_video_non_archived.id not in ids

    # Not in detail
    req = api_client.get(f"{base_url}{other_video_non_archived.id}/")
    assert req.status_code == 404


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("POST", 405),
        ("PUT", 405),
        ("PATCH", 405),
        ("DELETE", 405),
    ],
)
def test_anonymous_cannot_modify_videos(api_client, other_video, method, status):
    """Test that write methods return 405 on read-only endpoint."""
    base_url = get_base_url(other_video.category.event_id)
    url = f"{base_url}{other_video.id}/"
    assert api_client.generic(method, url).status_code == status
