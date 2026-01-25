import pytest


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/store/item_variants/"


@pytest.fixture
def variant_staff_api_client(api_client, create_user, password):
    """API client authenticated as a user with store item variant permissions."""
    permissions = [
        "store.view_storeitemvariant",
        "store.add_storeitemvariant",
        "store.change_storeitemvariant",
        "store.delete_storeitemvariant",
    ]
    user = create_user(is_staff=True, permissions=permissions)
    api_client.login(username=user.username, password=password)
    yield api_client
    api_client.logout()


@pytest.mark.django_db
def test_staff_can_list_item_variants(variant_staff_api_client, variant_item, store_item_variant):
    """Test that staff can list all store item variants."""
    base_url = get_base_url(variant_item.event_id)
    req = variant_staff_api_client.get(base_url)
    assert req.status_code == 200
    variant_ids = [v["id"] for v in req.data]
    assert store_item_variant.id in variant_ids


@pytest.mark.django_db
def test_staff_can_get_item_variant_detail(variant_staff_api_client, store_item_variant):
    """Test that staff can get store item variant details."""
    base_url = get_base_url(store_item_variant.item.event_id)
    req = variant_staff_api_client.get(f"{base_url}{store_item_variant.id}/")
    assert req.status_code == 200
    assert req.data["id"] == store_item_variant.id
    assert req.data["name"] == store_item_variant.name
    assert req.data["item"] == store_item_variant.item.id


@pytest.mark.django_db
def test_staff_can_create_item_variant(variant_staff_api_client, variant_item):
    """Test that staff can create a new store item variant."""
    base_url = get_base_url(variant_item.event_id)
    req = variant_staff_api_client.post(
        base_url,
        {
            "item": variant_item.id,
            "name": "New Size XXL",
        },
    )
    assert req.status_code == 201
    assert req.data["name"] == "New Size XXL"
    assert req.data["item"] == variant_item.id


@pytest.mark.django_db
def test_staff_can_update_item_variant(variant_staff_api_client, store_item_variant):
    """Test that staff can update a store item variant."""
    base_url = get_base_url(store_item_variant.item.event_id)
    req = variant_staff_api_client.patch(
        f"{base_url}{store_item_variant.id}/",
        {"name": "Updated Size Name"},
    )
    assert req.status_code == 200
    assert req.data["name"] == "Updated Size Name"


@pytest.mark.django_db
def test_staff_can_delete_item_variant(variant_staff_api_client, store_item_variant):
    """Test that staff can delete a store item variant."""
    base_url = get_base_url(store_item_variant.item.event_id)
    req = variant_staff_api_client.delete(f"{base_url}{store_item_variant.id}/")
    assert req.status_code == 204


@pytest.mark.django_db
def test_filter_by_event(variant_staff_api_client, variant_item, store_item_variant):
    """Test that variants are filtered by event."""
    base_url = get_base_url(variant_item.event_id)
    req = variant_staff_api_client.get(base_url)
    assert req.status_code == 200
    for variant in req.data:
        # All variants should belong to items in this event
        assert variant["item"] == variant_item.id


@pytest.mark.django_db
def test_filter_by_item(variant_staff_api_client, variant_item, store_item_variant, store_item_variant2):
    """Test filtering variants by item."""
    base_url = get_base_url(variant_item.event_id)
    req = variant_staff_api_client.get(f"{base_url}?item={variant_item.id}")
    assert req.status_code == 200
    for variant in req.data:
        assert variant["item"] == variant_item.id


@pytest.mark.django_db
def test_search_by_name(variant_staff_api_client, variant_item, store_item_variant):
    """Test searching variants by name."""
    base_url = get_base_url(variant_item.event_id)
    req = variant_staff_api_client.get(f"{base_url}?search={store_item_variant.name}")
    assert req.status_code == 200
    assert len(req.data) >= 1
    variant_names = [v["name"] for v in req.data]
    assert store_item_variant.name in variant_names
