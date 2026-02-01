import pytest


def get_base_url(event_id):
    return f"/api/v2/public/event/{event_id}/archive/video_categories/"


@pytest.mark.django_db
def test_anonymous_can_list_video_categories_for_archived_events(api_client, video_category):
    """Test that anonymous users can list video categories for archived events."""
    base_url = get_base_url(video_category.event_id)
    req = api_client.get(base_url)
    assert req.status_code == 200
    ids = [vc["id"] for vc in req.data]
    assert video_category.id in ids


@pytest.mark.django_db
def test_anonymous_can_get_video_category_detail(api_client, video_category):
    """Test that anonymous users can get video category details."""
    base_url = get_base_url(video_category.event_id)
    req = api_client.get(f"{base_url}{video_category.id}/")
    assert req.status_code == 200
    assert req.data["id"] == video_category.id


@pytest.mark.django_db
def test_anonymous_cannot_see_video_categories_for_non_archived_events(
    api_client, video_category_non_archived
):
    """Test that video categories for non-archived events are not visible."""
    base_url = get_base_url(video_category_non_archived.event_id)

    # Not in list
    req = api_client.get(base_url)
    assert req.status_code == 200
    ids = [vc["id"] for vc in req.data]
    assert video_category_non_archived.id not in ids

    # Not in detail
    req = api_client.get(f"{base_url}{video_category_non_archived.id}/")
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
def test_anonymous_cannot_modify_video_categories(api_client, video_category, method, status):
    """Test that write methods return 405 on read-only endpoint."""
    base_url = get_base_url(video_category.event_id)
    url = f"{base_url}{video_category.id}/"
    assert api_client.generic(method, url).status_code == status


@pytest.mark.django_db
def test_hidden_event_video_categories_not_in_list(
    api_client, hidden_archived_event, hidden_event_video_category
):
    """Video categories from hidden archived events should not appear in the list."""
    base_url = get_base_url(hidden_archived_event.id)
    req = api_client.get(base_url)
    assert req.status_code == 200
    assert len(req.data) == 0
