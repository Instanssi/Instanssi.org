import pytest


def get_base_url(event_id):
    return f"/api/v2/admin/event/{event_id}/arkisto/video_categories/"


@pytest.mark.django_db
def test_staff_can_list_video_categories(staff_api_client, video_category):
    """Test that staff can list all video categories."""
    base_url = get_base_url(video_category.event_id)
    req = staff_api_client.get(base_url)
    assert req.status_code == 200
    assert len(req.data) >= 1


@pytest.mark.django_db
def test_staff_can_get_video_category_detail(staff_api_client, video_category):
    """Test that staff can get video category details."""
    base_url = get_base_url(video_category.event_id)
    req = staff_api_client.get(f"{base_url}{video_category.id}/")
    assert req.status_code == 200
    assert req.data == {
        "id": video_category.id,
        "event": video_category.event_id,
        "name": video_category.name,
    }


@pytest.mark.django_db
def test_staff_can_create_video_category(staff_api_client, archived_event):
    """Test that staff can create a new video category."""
    base_url = get_base_url(archived_event.id)
    req = staff_api_client.post(
        base_url,
        {
            "event": archived_event.id,
            "name": "New Video Category",
        },
    )
    assert req.status_code == 201
    assert req.data == {
        "id": req.data["id"],
        "event": archived_event.id,
        "name": "New Video Category",
    }


@pytest.mark.django_db
def test_staff_can_update_video_category(staff_api_client, video_category):
    """Test that staff can update a video category."""
    base_url = get_base_url(video_category.event_id)
    req = staff_api_client.patch(f"{base_url}{video_category.id}/", {"name": "Updated Category Name"})
    assert req.status_code == 200
    assert req.data == {
        "id": video_category.id,
        "event": video_category.event_id,
        "name": "Updated Category Name",
    }


@pytest.mark.django_db
def test_staff_can_delete_video_category(staff_api_client, video_category):
    """Test that staff can delete a video category."""
    base_url = get_base_url(video_category.event_id)
    req = staff_api_client.delete(f"{base_url}{video_category.id}/")
    assert req.status_code == 204


@pytest.mark.django_db
def test_video_categories_filter_by_event(staff_api_client, archived_event, video_category):
    """Test that video categories are filtered by event."""
    base_url = get_base_url(archived_event.id)
    req = staff_api_client.get(base_url)
    assert req.status_code == 200
    for vc in req.data:
        assert vc["event"] == archived_event.id


@pytest.mark.django_db
def test_staff_can_see_video_categories_for_non_archived_events(
    staff_api_client, video_category_non_archived
):
    """Test that staff can see video categories for non-archived events."""
    base_url = get_base_url(video_category_non_archived.event_id)

    # Staff should see video categories for non-archived events in list
    staff_req = staff_api_client.get(base_url)
    assert staff_req.status_code == 200
    staff_ids = [vc["id"] for vc in staff_req.data]
    assert video_category_non_archived.id in staff_ids

    # Staff should be able to access non-archived video category detail
    detail_req = staff_api_client.get(f"{base_url}{video_category_non_archived.id}/")
    assert detail_req.status_code == 200


@pytest.mark.django_db
def test_video_categories_search_by_name(staff_api_client, video_category):
    """Test searching video categories by name."""
    base_url = get_base_url(video_category.event_id)
    search_term = video_category.name.split()[0]
    req = staff_api_client.get(f"{base_url}?search={search_term}")
    assert req.status_code == 200
    assert len(req.data) >= 1
