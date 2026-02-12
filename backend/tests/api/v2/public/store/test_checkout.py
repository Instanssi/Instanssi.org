"""Tests for the public store checkout endpoint (/api/v2/public/store/checkout/)."""

from unittest import mock

import pytest

from Instanssi.store.models import StoreTransaction
from Instanssi.store.utils.paytrail import NewPaymentResponse

CHECKOUT_URL = "/api/v2/public/store/checkout/"


@pytest.fixture
def valid_checkout_data(store_item):
    """Valid checkout data for creating a transaction."""
    return {
        "first_name": "Test",
        "last_name": "User",
        "company": "",
        "email": "test@example.com",
        "telephone": "",
        "mobile": "+358401234567",
        "street": "Test Street 123",
        "postal_code": "00100",
        "city": "Helsinki",
        "country": "FI",
        "information": "",
        "payment_method": 1,  # Paytrail
        "read_terms": True,
        "items": [{"item_id": store_item.id, "variant_id": None, "amount": 1}],
        "confirm": False,
    }


@pytest.mark.django_db
def test_checkout_validation_without_confirm(api_client, valid_checkout_data):
    """Test that checkout validation works without saving (confirm=False)."""
    req = api_client.post(CHECKOUT_URL, valid_checkout_data, format="json")
    assert req.status_code == 200


@pytest.mark.django_db
def test_checkout_requires_terms_accepted(api_client, valid_checkout_data):
    """Test that checkout requires terms to be accepted."""
    valid_checkout_data["read_terms"] = False
    req = api_client.post(CHECKOUT_URL, valid_checkout_data, format="json")
    assert req.status_code == 400
    assert "read_terms" in req.data


@pytest.mark.django_db
def test_checkout_requires_items(api_client, valid_checkout_data):
    """Test that checkout requires at least one item."""
    valid_checkout_data["items"] = []
    req = api_client.post(CHECKOUT_URL, valid_checkout_data, format="json")
    assert req.status_code == 400
    assert "items" in req.data


@pytest.mark.django_db
def test_checkout_validates_item_exists(api_client, valid_checkout_data):
    """Test that checkout validates items exist."""
    valid_checkout_data["items"] = [{"item_id": 99999, "variant_id": None, "amount": 1}]
    req = api_client.post(CHECKOUT_URL, valid_checkout_data, format="json")
    assert req.status_code == 400


@pytest.mark.django_db
def test_checkout_validates_item_available(api_client, valid_checkout_data, base_store_item):
    """Test that checkout validates items are available (unavailable items rejected)."""
    # Create an unavailable item
    unavailable_item = base_store_item()
    unavailable_item.available = False
    unavailable_item.save()

    valid_checkout_data["items"] = [{"item_id": unavailable_item.id, "variant_id": None, "amount": 1}]
    req = api_client.post(CHECKOUT_URL, valid_checkout_data, format="json")
    assert req.status_code == 400


@pytest.mark.django_db
def test_checkout_hidden_item_is_purchasable(api_client, valid_checkout_data, hidden_item):
    """Test that hidden items can still be purchased if you know the item ID."""
    # Hidden items are still available for purchase, they're just not shown in listings
    valid_checkout_data["items"] = [{"item_id": hidden_item.id, "variant_id": None, "amount": 1}]
    req = api_client.post(CHECKOUT_URL, valid_checkout_data, format="json")
    assert req.status_code == 200


@pytest.mark.django_db
def test_checkout_validates_variant_exists(api_client, valid_checkout_data, variant_item):
    """Test that checkout validates variant exists for item."""
    valid_checkout_data["items"] = [{"item_id": variant_item.id, "variant_id": 99999, "amount": 1}]
    req = api_client.post(CHECKOUT_URL, valid_checkout_data, format="json")
    assert req.status_code == 400


@pytest.mark.django_db
def test_checkout_with_variant(api_client, valid_checkout_data, variant_item, store_item_variant):
    """Test checkout with item variant."""
    valid_checkout_data["items"] = [
        {"item_id": variant_item.id, "variant_id": store_item_variant.id, "amount": 1}
    ]
    req = api_client.post(CHECKOUT_URL, valid_checkout_data, format="json")
    assert req.status_code == 200


@pytest.mark.django_db
def test_checkout_validates_amount(api_client, valid_checkout_data):
    """Test that checkout validates item amount."""
    valid_checkout_data["items"][0]["amount"] = 0
    req = api_client.post(CHECKOUT_URL, valid_checkout_data, format="json")
    assert req.status_code == 400


@pytest.mark.django_db
def test_checkout_validates_duplicate_items(api_client, valid_checkout_data, store_item):
    """Test that checkout validates no duplicate item/variant combinations."""
    valid_checkout_data["items"] = [
        {"item_id": store_item.id, "variant_id": None, "amount": 1},
        {"item_id": store_item.id, "variant_id": None, "amount": 1},
    ]
    req = api_client.post(CHECKOUT_URL, valid_checkout_data, format="json")
    assert req.status_code == 400


@pytest.mark.django_db
def test_checkout_creates_transaction_when_confirm_true(api_client, valid_checkout_data):
    """Test that checkout creates transaction when confirm=True."""
    valid_checkout_data["confirm"] = True
    initial_count = StoreTransaction.objects.count()
    with mock.patch("Instanssi.store.methods.paytrail.create_payment") as mock_create:
        mock_create.return_value = NewPaymentResponse(
            href="http://localhost/pay/test", request_id="req-1", transaction_id="ta-1"
        )
        req = api_client.post(CHECKOUT_URL, valid_checkout_data, format="json")
    assert req.status_code == 201
    assert "url" in req.data
    assert StoreTransaction.objects.count() == initial_count + 1


@pytest.mark.django_db
def test_checkout_does_not_create_transaction_when_confirm_false(api_client, valid_checkout_data):
    """Test that checkout does not create transaction when confirm=False."""
    valid_checkout_data["confirm"] = False
    initial_count = StoreTransaction.objects.count()
    req = api_client.post(CHECKOUT_URL, valid_checkout_data, format="json")
    assert req.status_code == 200
    assert StoreTransaction.objects.count() == initial_count


@pytest.mark.django_db
def test_checkout_required_fields(api_client):
    """Test that checkout validates required fields."""
    req = api_client.post(CHECKOUT_URL, {}, format="json")
    assert req.status_code == 400
    # Check required fields are mentioned in errors
    assert "first_name" in req.data
    assert "last_name" in req.data
    assert "email" in req.data
    assert "street" in req.data
    assert "postal_code" in req.data
    assert "city" in req.data
    assert "country" in req.data
    assert "payment_method" in req.data
    assert "read_terms" in req.data
    assert "items" in req.data
