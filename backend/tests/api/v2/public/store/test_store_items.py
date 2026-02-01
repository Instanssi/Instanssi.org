"""Tests for the public store items API endpoint (/api/v2/public/store/items/)."""

import pytest

PUBLIC_STORE_URL = "/api/v2/public/store/items/"


@pytest.mark.django_db
def test_public_can_list_available_items(api_client, store_item):
    """Test that public users can list available store items."""
    req = api_client.get(PUBLIC_STORE_URL)
    assert req.status_code == 200
    item_ids = [item["id"] for item in req.data]
    assert store_item.id in item_ids


@pytest.mark.django_db
def test_public_can_get_item_detail(api_client, store_item):
    """Test that public users can get store item details."""
    req = api_client.get(f"{PUBLIC_STORE_URL}{store_item.id}/")
    assert req.status_code == 200
    assert req.data["id"] == store_item.id


@pytest.mark.django_db
def test_public_cannot_see_hidden_items_without_secret_key(api_client, hidden_item):
    """Test that hidden items are not visible without secret_key."""
    req = api_client.get(PUBLIC_STORE_URL)
    assert req.status_code == 200
    item_ids = [item["id"] for item in req.data]
    assert hidden_item.id not in item_ids


@pytest.mark.django_db
def test_public_can_see_hidden_items_with_secret_key(api_client, hidden_item):
    """Test that hidden items are visible with correct secret_key."""
    req = api_client.get(f"{PUBLIC_STORE_URL}?secret_key={hidden_item.secret_key}")
    assert req.status_code == 200
    item_ids = [item["id"] for item in req.data]
    assert hidden_item.id in item_ids


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("POST", 405),
        ("PUT", 405),
        ("PATCH", 405),
        ("DELETE", 405),
    ],
)
def test_public_cannot_modify_items(api_client, store_item, method, status):
    """Test that write methods return 405 on read-only endpoint."""
    url = f"{PUBLIC_STORE_URL}{store_item.id}/"
    assert api_client.generic(method, url).status_code == status


@pytest.mark.django_db
def test_hidden_event_store_items_not_in_list(api_client, store_item, hidden_event_store_item):
    """Store items from hidden events should not appear in the list."""
    req = api_client.get(PUBLIC_STORE_URL)
    assert req.status_code == 200
    item_ids = [i["id"] for i in req.data]
    assert store_item.id in item_ids
    assert hidden_event_store_item.id not in item_ids
