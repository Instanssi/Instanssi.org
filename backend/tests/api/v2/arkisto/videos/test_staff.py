import pytest


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/archive/videos/"


@pytest.mark.django_db
def test_staff_can_list_videos(staff_api_client, other_video):
    """Test that staff can list all videos."""
    base_url = get_base_url(other_video.category.event_id)
    req = staff_api_client.get(base_url)
    assert req.status_code == 200
    assert len(req.data) >= 1


@pytest.mark.django_db
def test_staff_can_get_video_detail(staff_api_client, other_video):
    """Test that staff can get video details."""
    base_url = get_base_url(other_video.category.event_id)
    req = staff_api_client.get(f"{base_url}{other_video.id}/")
    assert req.status_code == 200
    assert req.data == {
        "id": other_video.id,
        "category": other_video.category_id,
        "name": other_video.name,
        "description": other_video.description,
        "youtube_url": {
            "video_id": "dQw4w9WgXcQ",
            "start": None,
        },
    }


@pytest.mark.django_db
def test_staff_can_create_video(staff_api_client, video_category):
    """Test that staff can create a new video."""
    base_url = get_base_url(video_category.event_id)
    req = staff_api_client.post(
        base_url,
        {
            "category": video_category.id,
            "name": "New Video",
            "description": "A brand new video",
            "youtube_url": "https://www.youtube.com/watch?v=abc123",
        },
    )
    assert req.status_code == 201
    assert req.data == {
        "id": req.data["id"],
        "category": video_category.id,
        "name": "New Video",
        "description": "A brand new video",
        "youtube_url": {
            "video_id": "abc123",
            "start": None,
        },
    }


@pytest.mark.django_db
def test_staff_can_update_video(staff_api_client, other_video):
    """Test that staff can update a video."""
    base_url = get_base_url(other_video.category.event_id)
    req = staff_api_client.patch(f"{base_url}{other_video.id}/", {"name": "Updated Video Name"})
    assert req.status_code == 200
    assert req.data == {
        "id": other_video.id,
        "category": other_video.category_id,
        "name": "Updated Video Name",
        "description": other_video.description,
        "youtube_url": {
            "video_id": "dQw4w9WgXcQ",
            "start": None,
        },
    }


@pytest.mark.django_db
def test_staff_can_delete_video(staff_api_client, other_video):
    """Test that staff can delete a video."""
    base_url = get_base_url(other_video.category.event_id)
    req = staff_api_client.delete(f"{base_url}{other_video.id}/")
    assert req.status_code == 204


@pytest.mark.django_db
def test_filter_by_event(staff_api_client, archived_event, other_video):
    """Test that videos are filtered by event."""
    base_url = get_base_url(archived_event.id)
    req = staff_api_client.get(base_url)
    assert req.status_code == 200
    for v in req.data:
        # All videos should belong to categories in this event
        assert v["category"] == other_video.category_id


@pytest.mark.django_db
def test_filter_by_category(staff_api_client, video_category, other_video):
    """Test filtering videos by category."""
    base_url = get_base_url(video_category.event_id)
    req = staff_api_client.get(f"{base_url}?category={video_category.id}")
    assert req.status_code == 200
    for v in req.data:
        assert v["category"] == video_category.id


@pytest.mark.django_db
def test_staff_can_see_videos_for_non_archived_events(staff_api_client, other_video_non_archived):
    """Test that staff can see videos for non-archived events."""
    base_url = get_base_url(other_video_non_archived.category.event_id)

    # Staff should see videos for non-archived events in list
    staff_req = staff_api_client.get(base_url)
    assert staff_req.status_code == 200
    staff_ids = [v["id"] for v in staff_req.data]
    assert other_video_non_archived.id in staff_ids

    # Staff should be able to access non-archived video detail
    detail_req = staff_api_client.get(f"{base_url}{other_video_non_archived.id}/")
    assert detail_req.status_code == 200


@pytest.mark.django_db
def test_search_by_name(staff_api_client, other_video):
    """Test searching videos by name."""
    base_url = get_base_url(other_video.category.event_id)
    search_term = other_video.name.split()[0]
    req = staff_api_client.get(f"{base_url}?search={search_term}")
    assert req.status_code == 200
    assert len(req.data) >= 1


@pytest.mark.django_db
def test_cannot_create_video_with_category_from_other_event(
    staff_api_client, event, other_event_video_category
):
    """Test that staff cannot create video with category from another event."""
    base_url = get_base_url(event.id)
    req = staff_api_client.post(
        base_url,
        {
            "category": other_event_video_category.id,
            "name": "Test Video",
            "description": "Test description",
            "youtube_url": "https://www.youtube.com/watch?v=abc123",
        },
    )
    assert req.status_code == 400
    assert "category" in req.data


@pytest.mark.django_db
def test_cannot_update_video_to_other_event_category(
    staff_api_client, other_video, other_event_video_category
):
    """Test that staff cannot update video to use category from another event."""
    base_url = get_base_url(other_video.category.event_id)
    req = staff_api_client.patch(
        f"{base_url}{other_video.id}/",
        {"category": other_event_video_category.id},
    )
    assert req.status_code == 400
    assert "category" in req.data
