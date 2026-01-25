from decimal import Decimal

import pytest


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/store/items/"


@pytest.fixture
def store_staff_api_client(api_client, create_user, password):
    """API client authenticated as a user with store permissions."""
    permissions = [
        "store.view_storeitem",
        "store.add_storeitem",
        "store.change_storeitem",
        "store.delete_storeitem",
    ]
    user = create_user(is_staff=True, permissions=permissions)
    api_client.login(username=user.username, password=password)
    yield api_client
    api_client.logout()


@pytest.mark.django_db
def test_staff_can_list_store_items(store_staff_api_client, store_item, hidden_item):
    """Test that staff can list all store items including hidden ones."""
    base_url = get_base_url(store_item.event_id)
    req = store_staff_api_client.get(base_url)
    assert req.status_code == 200
    item_ids = [item["id"] for item in req.data]
    # Staff can see both regular and hidden items
    assert store_item.id in item_ids
    assert hidden_item.id in item_ids


@pytest.mark.django_db
def test_staff_can_get_store_item_detail(store_staff_api_client, store_item):
    """Test that staff can get store item details."""
    base_url = get_base_url(store_item.event_id)
    req = store_staff_api_client.get(f"{base_url}{store_item.id}/")
    assert req.status_code == 200
    assert req.data["id"] == store_item.id
    assert req.data["name"] == store_item.name
    assert req.data["event"] == store_item.event_id


@pytest.mark.django_db
def test_staff_can_see_hidden_items_without_secret_key(store_staff_api_client, hidden_item):
    """Test that staff can see hidden items without secret_key."""
    base_url = get_base_url(hidden_item.event_id)

    # Staff should see hidden items in list without secret_key
    req = store_staff_api_client.get(base_url)
    assert req.status_code == 200
    item_ids = [item["id"] for item in req.data]
    assert hidden_item.id in item_ids

    # Staff should be able to access hidden item detail
    req = store_staff_api_client.get(f"{base_url}{hidden_item.id}/")
    assert req.status_code == 200
    assert req.data["id"] == hidden_item.id


@pytest.mark.django_db
def test_staff_can_create_store_item(store_staff_api_client, event):
    """Test that staff can create a new store item."""
    base_url = get_base_url(event.id)
    req = store_staff_api_client.post(
        base_url,
        {
            "event": event.id,
            "name": "New Test Item",
            "description": "A brand new store item",
            "price": "25.00",
            "max": 100,
            "available": True,
            "max_per_order": 5,
            "sort_index": 10,
            "discount_amount": -1,
            "discount_percentage": 0,
            "is_ticket": False,
            "is_secret": False,
            "secret_key": "",
        },
    )
    assert req.status_code == 201
    assert req.data["name"] == "New Test Item"
    assert Decimal(req.data["price"]) == Decimal("25.00")


@pytest.mark.django_db
def test_staff_can_update_store_item(store_staff_api_client, store_item):
    """Test that staff can update a store item."""
    base_url = get_base_url(store_item.event_id)
    req = store_staff_api_client.patch(
        f"{base_url}{store_item.id}/",
        {"name": "Updated Item Name", "price": "30.00"},
    )
    assert req.status_code == 200
    assert req.data["name"] == "Updated Item Name"
    assert Decimal(req.data["price"]) == Decimal("30.00")


@pytest.mark.django_db
def test_staff_can_delete_store_item(store_staff_api_client, store_item):
    """Test that staff can delete a store item."""
    base_url = get_base_url(store_item.event_id)
    req = store_staff_api_client.delete(f"{base_url}{store_item.id}/")
    assert req.status_code == 204


@pytest.mark.django_db
def test_filter_by_event(store_staff_api_client, event, store_item):
    """Test filtering store items by event."""
    base_url = get_base_url(event.id)
    req = store_staff_api_client.get(base_url)
    assert req.status_code == 200
    for item in req.data:
        assert item["event"] == event.id


@pytest.mark.django_db
def test_staff_can_make_item_hidden(store_staff_api_client, store_item):
    """Test that staff can make an item hidden."""
    base_url = get_base_url(store_item.event_id)
    req = store_staff_api_client.patch(
        f"{base_url}{store_item.id}/",
        {"is_secret": True, "secret_key": "test_secret"},
    )
    assert req.status_code == 200
    assert req.data["is_secret"] is True
    assert req.data["secret_key"] == "test_secret"


@pytest.mark.django_db
def test_store_item_includes_nested_variants(store_staff_api_client, variant_item, store_item_variant):
    """Test that store item response includes nested variants."""
    base_url = get_base_url(variant_item.event_id)
    req = store_staff_api_client.get(f"{base_url}{variant_item.id}/")
    assert req.status_code == 200
    assert "variants" in req.data
    assert len(req.data["variants"]) >= 1
    # Verify variant structure
    variant = req.data["variants"][0]
    assert "id" in variant
    assert "name" in variant
    assert "item" in variant  # Staff serializer includes item reference
    assert variant["item"] == variant_item.id
