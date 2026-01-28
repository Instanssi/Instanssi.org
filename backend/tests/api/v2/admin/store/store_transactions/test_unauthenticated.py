"""Tests for unauthenticated access to staff store transactions endpoint."""

import pytest


def get_base_url(event_id):
    return f"/api/v2/admin/event/{event_id}/store/transactions/"


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
def test_unauthenticated_transactions_list(api_client, store_item, method, status):
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
def test_unauthenticated_transactions_detail(api_client, transaction_item_a, store_item, method, status):
    """Test unauthenticated access to detail endpoint."""
    store_transaction = transaction_item_a.transaction
    base_url = get_base_url(store_item.event_id)
    url = f"{base_url}{store_transaction.id}/"
    assert api_client.generic(method, url).status_code == status
