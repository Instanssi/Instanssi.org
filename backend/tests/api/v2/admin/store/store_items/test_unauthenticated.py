import pytest


def get_base_url(event_id):
    return f"/api/v2/admin/event/{event_id}/store/items/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 401),  # Staff-only endpoint
        ("POST", 401),  # Create denied
        ("PUT", 401),  # Not allowed on list
        ("PATCH", 401),  # Not allowed on list
        ("DELETE", 401),  # Not allowed on list
    ],
)
def test_unauthenticated_store_items_list(api_client, event, method, status):
    """Test unauthenticated access to list endpoint (Not logged in).

    The event-scoped store items endpoint is staff-only.
    For public access, use /api/v2/public/store/items/ instead.
    """
    base_url = get_base_url(event.id)
    assert api_client.generic(method, base_url).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 401),  # Staff-only endpoint
        ("POST", 401),  # Not allowed on detail
        ("PUT", 401),  # Replace denied
        ("PATCH", 401),  # Update denied
        ("DELETE", 401),  # Delete denied
    ],
)
def test_unauthenticated_store_items_detail(api_client, store_item, method, status):
    """Test unauthenticated access to store item detail endpoint.

    The event-scoped store items endpoint is staff-only.
    """
    base_url = get_base_url(store_item.event_id)
    url = f"{base_url}{store_item.id}/"
    assert api_client.generic(method, url).status_code == status
