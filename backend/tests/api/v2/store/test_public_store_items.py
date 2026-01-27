"""Tests for the public store items API endpoint (/api/v2/store/items/)."""

import pytest

PUBLIC_STORE_URL = "/api/v2/store/items/"


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
    assert req.data["name"] == store_item.name


@pytest.mark.django_db
def test_public_cannot_see_hidden_items_without_secret_key(api_client, hidden_item):
    """Test that public users cannot see hidden items without secret_key."""
    req = api_client.get(PUBLIC_STORE_URL)
    assert req.status_code == 200
    item_ids = [item["id"] for item in req.data]
    assert hidden_item.id not in item_ids


@pytest.mark.django_db
def test_public_can_see_hidden_items_with_correct_secret_key(api_client, hidden_item):
    """Test that public users can see hidden items with correct secret_key."""
    req = api_client.get(f"{PUBLIC_STORE_URL}?secret_key={hidden_item.secret_key}")
    assert req.status_code == 200
    item_ids = [item["id"] for item in req.data]
    assert hidden_item.id in item_ids


@pytest.mark.django_db
def test_public_can_filter_by_event(api_client, store_item, event):
    """Test that public users can filter items by event."""
    req = api_client.get(f"{PUBLIC_STORE_URL}?event={event.id}")
    assert req.status_code == 200
    for item in req.data:
        assert item["event"] == event.id


@pytest.mark.django_db
def test_public_item_includes_variants(api_client, variant_item, store_item_variant):
    """Test that store items include nested variants."""
    req = api_client.get(f"{PUBLIC_STORE_URL}{variant_item.id}/")
    assert req.status_code == 200
    assert "variants" in req.data
    assert len(req.data["variants"]) >= 1


@pytest.mark.django_db
def test_public_item_includes_computed_fields(api_client, store_item):
    """Test that store items include computed fields like num_available."""
    req = api_client.get(f"{PUBLIC_STORE_URL}{store_item.id}/")
    assert req.status_code == 200
    assert "num_available" in req.data
    assert "discount_factor" in req.data
    assert "is_discount_available" in req.data


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("POST", 405),  # Method not allowed on read-only endpoint
        ("PUT", 405),
        ("PATCH", 405),
        ("DELETE", 405),
    ],
)
def test_public_cannot_modify_items(api_client, store_item, method, status):
    """Test that public users cannot modify store items."""
    url = f"{PUBLIC_STORE_URL}{store_item.id}/"
    assert api_client.generic(method, url).status_code == status


@pytest.mark.django_db
def test_public_item_does_not_expose_secret_fields(api_client, store_item):
    """Test that public endpoint does NOT expose sensitive fields."""
    req = api_client.get(f"{PUBLIC_STORE_URL}{store_item.id}/")
    assert req.status_code == 200
    # These fields should NOT be present in the public response
    assert "is_secret" not in req.data
    assert "secret_key" not in req.data
    assert "is_ticket" not in req.data
    assert "imagefile_original" not in req.data


@pytest.mark.django_db
def test_public_variant_does_not_expose_item_field(api_client, variant_item, store_item_variant):
    """Test that public variant serializer does NOT expose item field."""
    req = api_client.get(f"{PUBLIC_STORE_URL}{variant_item.id}/")
    assert req.status_code == 200
    assert "variants" in req.data
    assert len(req.data["variants"]) >= 1
    # Variant should only have id and name, not item
    variant = req.data["variants"][0]
    assert "id" in variant
    assert "name" in variant
    assert "item" not in variant
