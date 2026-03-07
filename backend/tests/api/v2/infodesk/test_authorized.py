"""Tests for authorized access to infodesk endpoints."""

import pytest


def get_base_url(event_id):
    return f"/api/v2/infodesk/event/{event_id}"


@pytest.fixture
def infodesk_view_client(api_client, create_user, password):
    """API client with infodesk view permission only."""
    user = create_user(is_staff=True, permissions=["infodesk.view_infodeskaccess"])
    api_client.login(username=user.username, password=password)
    yield api_client
    api_client.logout()


@pytest.fixture
def infodesk_full_client(api_client, create_user, password):
    """API client with both infodesk view and change permissions."""
    user = create_user(
        is_staff=True,
        permissions=["infodesk.view_infodeskaccess", "infodesk.change_infodeskaccess"],
    )
    api_client.login(username=user.username, password=password)
    yield api_client
    api_client.logout()


@pytest.mark.django_db
def test_can_list_transactions(infodesk_view_client, transaction_item_a, store_item):
    base = get_base_url(store_item.event_id)
    response = infodesk_view_client.get(f"{base}/transactions/?limit=25")
    assert response.status_code == 200
    assert response.data["count"] >= 1


TRANSACTION_FIELDS = {
    "id",
    "time_created",
    "time_paid",
    "time_cancelled",
    "firstname",
    "lastname",
    "email",
    "company",
    "telephone",
    "mobile",
    "information",
    "is_paid",
    "is_cancelled",
    "is_pending",
    "is_delivered",
    "full_name",
    "status_text",
}

TRANSACTION_ITEM_FIELDS = {
    "id",
    "key",
    "item",
    "variant",
    "transaction",
    "time_delivered",
    "purchase_price",
    "is_delivered",
    "item_name",
    "variant_name",
    "transaction_full_name",
    "transaction_is_paid",
}

# Fields that must NEVER appear in infodesk responses.
TRANSACTION_FORBIDDEN_FIELDS = {
    "token",
    "key",
    "street",
    "postalcode",
    "city",
    "country",
    "payment_method_name",
}


@pytest.mark.django_db
def test_can_get_transaction_detail(infodesk_view_client, transaction_item_a, store_item):
    base = get_base_url(store_item.event_id)
    store_transaction = transaction_item_a.transaction
    response = infodesk_view_client.get(f"{base}/transactions/{store_transaction.id}/")
    assert response.status_code == 200
    assert response.data["id"] == store_transaction.id
    assert response.data["firstname"] == store_transaction.firstname
    assert response.data["lastname"] == store_transaction.lastname
    assert response.data["is_paid"] is True
    assert response.data["full_name"] == store_transaction.full_name


@pytest.mark.django_db
def test_can_search_transactions(infodesk_view_client, transaction_item_a, store_item):
    base = get_base_url(store_item.event_id)
    store_transaction = transaction_item_a.transaction
    response = infodesk_view_client.get(
        f"{base}/transactions/?limit=25&search={store_transaction.firstname}"
    )
    assert response.status_code == 200
    assert response.data["count"] >= 1


@pytest.mark.django_db
def test_can_list_transaction_items(infodesk_view_client, transaction_item_a, store_item):
    base = get_base_url(store_item.event_id)
    response = infodesk_view_client.get(f"{base}/transaction_items/?limit=25")
    assert response.status_code == 200
    assert response.data["count"] >= 1


@pytest.mark.django_db
def test_can_get_transaction_item_detail(infodesk_view_client, transaction_item_a, store_item):
    base = get_base_url(store_item.event_id)
    response = infodesk_view_client.get(f"{base}/transaction_items/{transaction_item_a.id}/")
    assert response.status_code == 200
    assert response.data["id"] == transaction_item_a.id
    assert response.data["key"] == transaction_item_a.key
    assert response.data["item_name"] == transaction_item_a.item.name
    assert response.data["transaction_full_name"] == transaction_item_a.transaction.full_name
    assert response.data["transaction_is_paid"] is True


@pytest.mark.django_db
def test_can_search_transaction_items_by_key(infodesk_view_client, transaction_item_a, store_item):
    base = get_base_url(store_item.event_id)
    response = infodesk_view_client.get(
        f"{base}/transaction_items/?limit=25&search={transaction_item_a.key}"
    )
    assert response.status_code == 200
    assert response.data["count"] >= 1


@pytest.mark.django_db
def test_can_filter_transaction_items_by_transaction(infodesk_view_client, transaction_item_a, store_item):
    base = get_base_url(store_item.event_id)
    response = infodesk_view_client.get(
        f"{base}/transaction_items/?limit=25&transaction={transaction_item_a.transaction_id}"
    )
    assert response.status_code == 200
    assert response.data["count"] >= 1


@pytest.mark.django_db
def test_view_only_cannot_mark_delivered(infodesk_view_client, transaction_item_a, store_item):
    """User with view permission only cannot mark items as delivered."""
    base = get_base_url(store_item.event_id)
    response = infodesk_view_client.post(f"{base}/transaction_items/{transaction_item_a.id}/mark_delivered/")
    assert response.status_code == 403


@pytest.mark.django_db
def test_can_mark_delivered(infodesk_full_client, claimable_ticket, store_item):
    """User with change permission can mark items as delivered."""
    assert claimable_ticket.time_delivered is None
    base = get_base_url(store_item.event_id)
    response = infodesk_full_client.post(f"{base}/transaction_items/{claimable_ticket.id}/mark_delivered/")
    assert response.status_code == 200
    assert response.data["is_delivered"] is True
    claimable_ticket.refresh_from_db()
    assert claimable_ticket.time_delivered is not None


@pytest.mark.django_db
def test_mark_delivered_is_idempotent(infodesk_full_client, claimable_ticket, store_item):
    """Marking an already-delivered item should be a no-op (not update time_delivered)."""
    base = get_base_url(store_item.event_id)
    url = f"{base}/transaction_items/{claimable_ticket.id}/mark_delivered/"
    first_response = infodesk_full_client.post(url)
    assert first_response.status_code == 200
    first_time = first_response.data["time_delivered"]

    second_response = infodesk_full_client.post(url)
    assert second_response.status_code == 200
    assert second_response.data["time_delivered"] == first_time


@pytest.mark.django_db
def test_transactions_are_read_only(infodesk_full_client, transaction_item_a, store_item):
    """Infodesk endpoints are read-only for transactions (no POST/PUT/PATCH/DELETE)."""
    base = get_base_url(store_item.event_id)
    base_url = f"{base}/transactions/"
    assert infodesk_full_client.post(base_url, {}).status_code == 405
    detail_url = f"{base_url}{transaction_item_a.transaction_id}/"
    assert infodesk_full_client.put(detail_url, {}).status_code == 405
    assert infodesk_full_client.patch(detail_url, {}).status_code == 405
    assert infodesk_full_client.delete(detail_url).status_code == 405


@pytest.mark.django_db
def test_transaction_items_are_read_only(infodesk_full_client, transaction_item_a, store_item):
    """Infodesk endpoints are read-only for transaction items (no POST/PUT/PATCH/DELETE)."""
    base = get_base_url(store_item.event_id)
    base_url = f"{base}/transaction_items/"
    assert infodesk_full_client.post(base_url, {}).status_code == 405
    detail_url = f"{base_url}{transaction_item_a.id}/"
    assert infodesk_full_client.put(detail_url, {}).status_code == 405
    assert infodesk_full_client.patch(detail_url, {}).status_code == 405
    assert infodesk_full_client.delete(detail_url).status_code == 405


@pytest.mark.django_db
def test_transaction_exposes_only_allowed_fields(infodesk_view_client, transaction_item_a, store_item):
    """Transaction response must contain exactly the allowed fields and no sensitive data."""
    base = get_base_url(store_item.event_id)
    store_transaction = transaction_item_a.transaction
    response = infodesk_view_client.get(f"{base}/transactions/{store_transaction.id}/")
    assert response.status_code == 200
    returned_fields = set(response.data.keys())
    assert returned_fields == TRANSACTION_FIELDS
    assert returned_fields.isdisjoint(TRANSACTION_FORBIDDEN_FIELDS)


@pytest.mark.django_db
def test_transaction_item_exposes_only_allowed_fields(infodesk_view_client, transaction_item_a, store_item):
    """Transaction item response must contain exactly the allowed fields and no sensitive data."""
    base = get_base_url(store_item.event_id)
    response = infodesk_view_client.get(f"{base}/transaction_items/{transaction_item_a.id}/")
    assert response.status_code == 200
    returned_fields = set(response.data.keys())
    assert returned_fields == TRANSACTION_ITEM_FIELDS
