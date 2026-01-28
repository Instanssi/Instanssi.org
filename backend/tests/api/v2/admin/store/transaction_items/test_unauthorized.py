"""Tests for unauthorized access to staff transaction items endpoint."""

import pytest


def get_base_url(event_id):
    return f"/api/v2/admin/event/{event_id}/store/transaction_items/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 403),
        ("POST", 403),
        ("PUT", 403),
        ("PATCH", 403),
        ("DELETE", 403),
    ],
)
def test_unauthorized_transaction_items_list(auth_client, store_item, method, status):
    """Test unauthorized access to list endpoint (Logged in, but no permissions)."""
    base_url = get_base_url(store_item.event_id)
    assert auth_client.generic(method, base_url).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 403),
        ("POST", 403),
        ("PUT", 403),
        ("PATCH", 403),
        ("DELETE", 403),
    ],
)
def test_unauthorized_transaction_items_detail(auth_client, transaction_item_a, store_item, method, status):
    """Test unauthorized access to detail endpoint (Logged in, but no permissions)."""
    base_url = get_base_url(store_item.event_id)
    url = f"{base_url}{transaction_item_a.id}/"
    assert auth_client.generic(method, url).status_code == status
