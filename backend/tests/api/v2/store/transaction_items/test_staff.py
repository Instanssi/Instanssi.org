"""Tests for the staff transaction items endpoint."""

from datetime import datetime
from datetime import timezone as dt_tz

import pytest
from django.conf import settings


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/store/transaction_items/"


@pytest.fixture
def store_staff_api_client(api_client, create_user, password):
    """API client authenticated as a user with store permissions."""
    permissions = [
        "store.view_transactionitem",
        "store.add_transactionitem",
        "store.change_transactionitem",
        "store.delete_transactionitem",
    ]
    user = create_user(is_staff=True, permissions=permissions)
    api_client.login(username=user.username, password=password)
    yield api_client
    api_client.logout()


@pytest.mark.django_db
def test_staff_can_list_transaction_items(store_staff_api_client, transaction_item_a, store_item):
    """Test that staff can list all transaction items."""
    base_url = get_base_url(store_item.event_id)
    req = store_staff_api_client.get(base_url)
    assert req.status_code == 200
    item_ids = [item["id"] for item in req.data]
    assert transaction_item_a.id in item_ids


@pytest.mark.django_db
def test_staff_can_get_transaction_item_detail(store_staff_api_client, transaction_item_a, store_item):
    """Test that staff can get transaction item details."""
    base_url = get_base_url(store_item.event_id)
    req = store_staff_api_client.get(f"{base_url}{transaction_item_a.id}/")
    assert req.status_code == 200
    assert req.data["id"] == transaction_item_a.id
    assert req.data["key"] == transaction_item_a.key


@pytest.mark.django_db
def test_staff_can_mark_item_as_delivered(store_staff_api_client, transaction_item_a, store_item):
    """Test that staff can mark a transaction item as delivered."""
    base_url = get_base_url(store_item.event_id)
    delivery_time = datetime(2025, 6, 15, 14, 30, 0, tzinfo=dt_tz.utc)
    req = store_staff_api_client.patch(
        f"{base_url}{transaction_item_a.id}/",
        {"time_delivered": delivery_time.isoformat()},
    )
    assert req.status_code == 200
    assert req.data["time_delivered"] == delivery_time.astimezone(settings.ZONE_INFO).isoformat()


@pytest.mark.django_db
def test_transaction_item_includes_is_delivered_field(
    store_staff_api_client, transaction_item_a, store_item
):
    """Test that transaction item response includes is_delivered computed field."""
    base_url = get_base_url(store_item.event_id)
    req = store_staff_api_client.get(f"{base_url}{transaction_item_a.id}/")
    assert req.status_code == 200
    assert "is_delivered" in req.data
    # transaction_item_a fixture has time_delivered set
    assert req.data["is_delivered"] is True


@pytest.mark.django_db
def test_staff_can_filter_by_transaction(
    store_staff_api_client, transaction_item_a, store_transaction, store_item
):
    """Test that staff can filter transaction items by transaction."""
    base_url = get_base_url(store_item.event_id)
    req = store_staff_api_client.get(f"{base_url}?transaction={store_transaction.id}")
    assert req.status_code == 200
    for item in req.data:
        assert item["transaction"] == store_transaction.id


@pytest.mark.django_db
def test_staff_can_filter_by_item(store_staff_api_client, transaction_item_a, store_item):
    """Test that staff can filter transaction items by store item."""
    base_url = get_base_url(store_item.event_id)
    req = store_staff_api_client.get(f"{base_url}?item={store_item.id}")
    assert req.status_code == 200
    for item in req.data:
        assert item["item"] == store_item.id


@pytest.mark.django_db
def test_staff_can_search_by_key(store_staff_api_client, transaction_item_a, store_item):
    """Test that staff can search transaction items by key."""
    base_url = get_base_url(store_item.event_id)
    req = store_staff_api_client.get(f"{base_url}?search={transaction_item_a.key[:8]}")
    assert req.status_code == 200


@pytest.mark.django_db
def test_unauthenticated_cannot_access_transaction_items(api_client, store_item):
    """Test that unauthenticated users cannot access transaction items endpoint."""
    base_url = get_base_url(store_item.event_id)
    req = api_client.get(base_url)
    assert req.status_code == 401


@pytest.mark.django_db
def test_unauthorized_cannot_access_transaction_items(auth_client, store_item):
    """Test that users without permissions cannot access transaction items endpoint."""
    base_url = get_base_url(store_item.event_id)
    req = auth_client.get(base_url)
    assert req.status_code == 403


@pytest.mark.django_db
def test_cannot_update_transaction_item_to_other_event_item(
    store_staff_api_client, transaction_item_a, store_item, other_event_store_item
):
    """Test that staff cannot update transaction item to use item from another event."""
    base_url = get_base_url(store_item.event_id)
    req = store_staff_api_client.patch(
        f"{base_url}{transaction_item_a.id}/",
        {"item": other_event_store_item.id},
    )
    assert req.status_code == 400
    assert "item" in req.data
