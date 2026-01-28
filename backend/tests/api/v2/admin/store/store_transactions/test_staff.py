"""Tests for the staff store transactions endpoint."""

import pytest


def get_base_url(event_id):
    return f"/api/v2/admin/event/{event_id}/store/transactions/"


@pytest.fixture
def store_staff_api_client(api_client, create_user, password):
    """API client authenticated as a user with store permissions."""
    permissions = [
        "store.view_storetransaction",
        "store.add_storetransaction",
        "store.change_storetransaction",
        "store.delete_storetransaction",
    ]
    user = create_user(is_staff=True, permissions=permissions)
    api_client.login(username=user.username, password=password)
    yield api_client
    api_client.logout()


@pytest.mark.django_db
def test_staff_can_list_transactions(store_staff_api_client, transaction_item_a, store_item):
    """Test that staff can list all transactions."""
    # transaction_item_a links store_transaction to store_item's event
    base_url = get_base_url(store_item.event_id)
    req = store_staff_api_client.get(base_url)
    assert req.status_code == 200
    assert len(req.data) >= 1


@pytest.mark.django_db
def test_staff_can_get_transaction_detail(store_staff_api_client, transaction_item_a, store_item):
    """Test that staff can get transaction details."""
    # transaction_item_a links store_transaction to store_item's event
    store_transaction = transaction_item_a.transaction
    base_url = get_base_url(store_item.event_id)
    req = store_staff_api_client.get(f"{base_url}{store_transaction.id}/")
    assert req.status_code == 200
    assert req.data["id"] == store_transaction.id
    assert req.data["firstname"] == store_transaction.firstname
    assert req.data["lastname"] == store_transaction.lastname


@pytest.mark.django_db
def test_staff_can_update_transaction(store_staff_api_client, transaction_item_a, store_item):
    """Test that staff can update a transaction."""
    store_transaction = transaction_item_a.transaction
    base_url = get_base_url(store_item.event_id)
    req = store_staff_api_client.patch(
        f"{base_url}{store_transaction.id}/",
        {"firstname": "Updated", "lastname": "Name"},
    )
    assert req.status_code == 200
    assert req.data["firstname"] == "Updated"
    assert req.data["lastname"] == "Name"


@pytest.mark.django_db
def test_staff_can_search_transactions(store_staff_api_client, transaction_item_a, store_item):
    """Test that staff can search transactions by name/email."""
    store_transaction = transaction_item_a.transaction
    base_url = get_base_url(store_item.event_id)
    req = store_staff_api_client.get(f"{base_url}?search={store_transaction.firstname}")
    assert req.status_code == 200


@pytest.mark.django_db
def test_transaction_includes_computed_fields(store_staff_api_client, transaction_item_a, store_item):
    """Test that transaction response includes computed fields."""
    store_transaction = transaction_item_a.transaction
    base_url = get_base_url(store_item.event_id)
    req = store_staff_api_client.get(f"{base_url}{store_transaction.id}/")
    assert req.status_code == 200
    assert "is_paid" in req.data
    assert "is_cancelled" in req.data
    assert "is_pending" in req.data
    assert "is_delivered" in req.data
    assert "full_name" in req.data
    assert "status_text" in req.data
    assert "total_price" in req.data


@pytest.mark.django_db
def test_transaction_includes_nested_events_and_receipts(
    store_staff_api_client, transaction_item_a, store_item
):
    """Test that transaction response includes nested events and receipts."""
    store_transaction = transaction_item_a.transaction
    base_url = get_base_url(store_item.event_id)
    req = store_staff_api_client.get(f"{base_url}{store_transaction.id}/")
    assert req.status_code == 200
    # Check nested fields are present (may be empty lists)
    assert "events" in req.data
    assert "receipts" in req.data
    assert isinstance(req.data["events"], list)
    assert isinstance(req.data["receipts"], list)
