"""Tests for unauthenticated access to staff receipts endpoint."""

import pytest


def get_base_url(event_id):
    return f"/api/v2/admin/event/{event_id}/store/receipts/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 401),
        ("POST", 401),
        ("PUT", 401),
        ("PATCH", 401),
        ("DELETE", 401),
    ],
)
def test_unauthenticated_receipts_list(api_client, store_item, method, status):
    """Test unauthenticated access to list endpoint."""
    base_url = get_base_url(store_item.event_id)
    assert api_client.generic(method, base_url).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 401),
        ("POST", 401),
        ("PUT", 401),
        ("PATCH", 401),
        ("DELETE", 401),
    ],
)
def test_unauthenticated_receipts_detail(api_client, store_receipt, transaction_item_a, method, status):
    """Test unauthenticated access to detail endpoint."""
    base_url = get_base_url(transaction_item_a.item.event_id)
    url = f"{base_url}{store_receipt.id}/"
    assert api_client.generic(method, url).status_code == status


@pytest.mark.django_db
def test_unauthenticated_cannot_resend_receipt(api_client, store_receipt, transaction_item_a):
    """Test unauthenticated access to resend action."""
    base_url = get_base_url(transaction_item_a.item.event_id)
    req = api_client.post(f"{base_url}{store_receipt.id}/resend/")
    assert req.status_code == 401
