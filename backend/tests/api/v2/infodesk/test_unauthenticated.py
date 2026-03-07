"""Tests for unauthenticated access to infodesk endpoints."""

import pytest


def get_base_url(event_id):
    return f"/api/v2/infodesk/event/{event_id}"


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
    url = f"{get_base_url(store_item.event_id)}/transactions/"
    assert api_client.generic(method, url).status_code == status


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
    url = f"{get_base_url(store_item.event_id)}/transactions/{transaction_item_a.transaction_id}/"
    assert api_client.generic(method, url).status_code == status


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
def test_unauthenticated_transaction_items_list(api_client, store_item, method, status):
    url = f"{get_base_url(store_item.event_id)}/transaction_items/"
    assert api_client.generic(method, url).status_code == status


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
def test_unauthenticated_transaction_items_detail(
    api_client, transaction_item_a, store_item, method, status
):
    url = f"{get_base_url(store_item.event_id)}/transaction_items/{transaction_item_a.id}/"
    assert api_client.generic(method, url).status_code == status


@pytest.mark.django_db
def test_unauthenticated_mark_delivered(api_client, transaction_item_a, store_item):
    url = f"{get_base_url(store_item.event_id)}/transaction_items/{transaction_item_a.id}/mark_delivered/"
    assert api_client.post(url).status_code == 401
