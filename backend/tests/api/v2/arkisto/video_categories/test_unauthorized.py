import pytest


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/archive/video_categories/"


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
def test_unauthorized_video_categories_list(auth_client, archived_event, method, status):
    """Test unauthorized access to list endpoint (Logged in without permissions).

    The video categories endpoint allows public read access for archived events
    but requires arkisto.add/change/delete_othervideocategory permissions for writes.
    """
    base_url = get_base_url(archived_event.id)
    assert auth_client.generic(method, base_url).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 200),  # Public read access to existing video category
        ("POST", 403),  # Not allowed on detail
        ("PUT", 403),  # Replace denied
        ("PATCH", 403),  # Update denied
        ("DELETE", 403),  # Delete denied
    ],
)
def test_unauthorized_video_categories_detail(auth_client, video_category, method, status):
    """Test unauthorized access to existing video category detail endpoint.

    The video categories endpoint allows public read access for archived events
    but requires arkisto.add/change/delete_othervideocategory permissions for writes.
    """
    base_url = get_base_url(video_category.event_id)
    url = f"{base_url}{video_category.id}/"
    assert auth_client.generic(method, url).status_code == status


@pytest.mark.django_db
def test_unauthorized_user_cannot_see_video_categories_for_non_archived_events(
    auth_client, video_category_non_archived
):
    """Test that users without permissions cannot see video categories for non-archived events."""
    base_url = get_base_url(video_category_non_archived.event_id)

    # Users without permissions should not see video categories for non-archived events
    req = auth_client.get(base_url)
    assert req.status_code == 200
    ids = [vc["id"] for vc in req.data]
    assert video_category_non_archived.id not in ids

    # Users without permissions should get 404 for non-archived video category detail
    detail_req = auth_client.get(f"{base_url}{video_category_non_archived.id}/")
    assert detail_req.status_code == 404
