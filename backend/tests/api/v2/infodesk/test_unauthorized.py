"""Tests for unauthorized access to infodesk endpoints (logged in, but no permissions)."""

import pytest


def get_base_url(event_id):
    return f"/api/v2/infodesk/event/{event_id}"


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
def test_unauthorized_transactions_list(auth_client, store_item, method, status):
    url = f"{get_base_url(store_item.event_id)}/transactions/"
    assert auth_client.generic(method, url).status_code == status


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
def test_unauthorized_transactions_detail(auth_client, transaction_item_a, store_item, method, status):
    url = f"{get_base_url(store_item.event_id)}/transactions/{transaction_item_a.transaction_id}/"
    assert auth_client.generic(method, url).status_code == status


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
    url = f"{get_base_url(store_item.event_id)}/transaction_items/"
    assert auth_client.generic(method, url).status_code == status


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
    url = f"{get_base_url(store_item.event_id)}/transaction_items/{transaction_item_a.id}/"
    assert auth_client.generic(method, url).status_code == status


@pytest.mark.django_db
def test_unauthorized_mark_delivered(auth_client, transaction_item_a, store_item):
    url = f"{get_base_url(store_item.event_id)}/transaction_items/{transaction_item_a.id}/mark_delivered/"
    assert auth_client.post(url).status_code == 403
