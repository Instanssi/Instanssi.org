import pytest


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/store/items/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 403),  # Staff-only endpoint, no view permission
        ("POST", 403),  # Create denied (authenticated but no permissions)
        ("PUT", 403),  # Not allowed on list
        ("PATCH", 403),  # Not allowed on list
        ("DELETE", 403),  # Not allowed on list
    ],
)
def test_unauthorized_store_items_list(auth_client, event, method, status):
    """Test unauthorized access to list endpoint (Logged in without permissions).

    The event-scoped store items endpoint is staff-only.
    Requires store.view/add/change/delete_storeitem permissions.
    """
    base_url = get_base_url(event.id)
    assert auth_client.generic(method, base_url).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 403),  # Staff-only endpoint, no view permission
        ("POST", 403),  # Not allowed on detail
        ("PUT", 403),  # Replace denied
        ("PATCH", 403),  # Update denied
        ("DELETE", 403),  # Delete denied
    ],
)
def test_unauthorized_store_items_detail(auth_client, store_item, method, status):
    """Test unauthorized access to existing store item detail endpoint.

    The event-scoped store items endpoint is staff-only.
    Requires store.view/add/change/delete_storeitem permissions.
    """
    base_url = get_base_url(store_item.event_id)
    url = f"{base_url}{store_item.id}/"
    assert auth_client.generic(method, url).status_code == status
