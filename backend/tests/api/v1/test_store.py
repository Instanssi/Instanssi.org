from unittest import mock
from unittest.mock import ANY

import pytest
from rest_framework.exceptions import ErrorDetail

from Instanssi.store.methods import PaymentMethod
from Instanssi.store.models import StoreTransaction


@pytest.mark.django_db
def test_store_api_items_get_ok(api_client, store_item, discount_item, hidden_item):
    url = "/api/v1/store_items/"
    req = api_client.get(url)
    assert req.status_code == 200
    assert req.data == [
        {
            "available": True,
            "description": ANY,
            "discount_amount": -1,
            "discount_factor": 1.0,
            "discount_percentage": 0,
            "event": 1,
            "id": 1,
            "imagefile_original_url": ANY,
            "imagefile_thumbnail_url": ANY,
            "is_discount_available": False,
            "max": 50,
            "max_per_order": 5,
            "name": "Test item 1",
            "num_available": 5,
            "price": "20.00",
            "sort_index": 0,
            "variants": [],
        },
        {
            "available": True,
            "description": ANY,
            "discount_amount": 5,
            "discount_factor": 0.5,
            "discount_percentage": 50,
            "event": 1,
            "id": 2,
            "imagefile_original_url": ANY,
            "imagefile_thumbnail_url": ANY,
            "is_discount_available": True,
            "max": 50,
            "max_per_order": 5,
            "name": "Test item 1",
            "num_available": 5,
            "price": "20.00",
            "sort_index": 0,
            "variants": [],
        },
    ]


@pytest.mark.django_db
def test_store_api_transaction_post_empty_error(api_client):
    url = "/api/v1/store_transaction/"
    req = api_client.post(url, data={})
    assert req.status_code == 400


@pytest.mark.django_db
def test_store_api_transaction_post_no_items_error(transaction_base, api_client):
    url = "/api/v1/store_transaction/"
    req = api_client.post(
        url, data={**transaction_base, "read_terms": True, "items": [], "payment_method": 1}
    )
    assert req.status_code == 400
    assert req.data == {
        "items": [ErrorDetail(string="Shopping cart must contain at least one item", code="invalid")]
    }


@pytest.mark.django_db
def test_store_api_transaction_post_dup_item(transaction_base, api_client, variant_item, store_item_variant):
    url = "/api/v1/store_transaction/"
    req = api_client.post(
        url,
        data={
            **transaction_base,
            "read_terms": True,
            "payment_method": 1,
            "items": [
                {"item_id": variant_item.id, "variant_id": store_item_variant.id, "amount": 1},
                {"item_id": variant_item.id, "variant_id": store_item_variant.id, "amount": 1},
            ],
        },
    )
    assert req.status_code == 400
    assert req.data == {
        "items": [ErrorDetail(string="Same product variant can only be in cart once", code="invalid")]
    }


@pytest.mark.django_db
def test_store_api_transaction_post_dup_variant(transaction_base, api_client, store_item):
    url = "/api/v1/store_transaction/"
    req = api_client.post(
        url,
        data={
            **transaction_base,
            "read_terms": True,
            "payment_method": 1,
            "items": [
                {"item_id": store_item.id, "variant_id": None, "amount": 1},
                {"item_id": store_item.id, "variant_id": None, "amount": 1},
            ],
        },
    )
    assert req.status_code == 400
    assert req.data == {
        "items": [ErrorDetail(string="Same product variant can only be in cart once", code="invalid")]
    }


@pytest.mark.django_db
def test_store_api_transaction_post_zero_item_count(
    transaction_base, api_client, variant_item, store_item_variant
):
    url = "/api/v1/store_transaction/"
    req = api_client.post(
        url,
        data={
            **transaction_base,
            "read_terms": True,
            "payment_method": 1,
            "items": [
                {"item_id": variant_item.id, "variant_id": store_item_variant.id, "amount": 0},
            ],
        },
    )
    assert req.status_code == 400
    assert req.data == {
        "items": [
            {
                "amount": [
                    ErrorDetail(string="Ensure this value is greater than or equal to 1.", code="min_value")
                ]
            }
        ]
    }


@pytest.mark.django_db
def test_store_api_transaction_post_hit_max_item_count(transaction_base, api_client, store_item):
    url = "/api/v1/store_transaction/"
    req = api_client.post(
        url,
        data={
            **transaction_base,
            "read_terms": True,
            "payment_method": 1,
            "items": [
                {"item_id": store_item.id, "variant_id": None, "amount": 6},
            ],
        },
    )
    assert req.status_code == 400
    assert req.data == {
        "items": [
            {
                "non_field_errors": [
                    ErrorDetail(
                        string="Product Test item 1 is not available in sufficient quantity", code="invalid"
                    )
                ]
            }
        ]
    }


@pytest.mark.django_db
def test_store_api_transaction_post_out_of_stock(transaction_base, api_client, store_item):
    store_item.max = 1
    store_item.save()

    url = "/api/v1/store_transaction/"
    req = api_client.post(
        url,
        data={
            **transaction_base,
            "read_terms": True,
            "payment_method": 1,
            "items": [
                {"item_id": store_item.id, "variant_id": None, "amount": 2},
            ],
        },
    )
    assert req.status_code == 400
    assert req.data == {
        "items": [
            {
                "non_field_errors": [
                    ErrorDetail(
                        string="Product Test item 1 is not available in sufficient quantity", code="invalid"
                    )
                ]
            }
        ]
    }


@pytest.mark.django_db
def test_store_api_transaction_post_ok_no_save(transaction_base, api_client, store_item):
    url = "/api/v1/store_transaction/"
    req = api_client.post(
        url,
        data={
            **transaction_base,
            "read_terms": True,
            "payment_method": 1,
            "items": [
                {"item_id": store_item.id, "variant_id": None, "amount": 2},
            ],
        },
    )
    assert req.status_code == 200
    assert req.data is None

    # Transaction is okay to send (valid), but request did not include "save" field.
    # Therefore nothing was saved.
    assert StoreTransaction.objects.filter(email=transaction_base["email"]).count() == 0


@pytest.mark.django_db
@mock.patch("Instanssi.api.v1.viewsets.store.begin_payment_process")
def test_store_api_transaction_post_ok_with_save(mocked_payment, transaction_base, api_client, store_item):
    mocked_payment.return_value = "/test/path/"

    url = "/api/v1/store_transaction/"
    req = api_client.post(
        url,
        data={
            **transaction_base,
            "read_terms": True,
            "payment_method": 1,
            "items": [
                {"item_id": store_item.id, "variant_id": None, "amount": 2},
            ],
            "save": True,  # !!!
        },
    )
    assert req.status_code == 201
    assert req.data == {"url": "/test/path/"}

    mocked_payment.assert_called_once_with(ANY, PaymentMethod.PAYTRAIL, ANY)

    # Transaction is okay to send (valid), and save field was included -- transaction made!
    assert StoreTransaction.objects.filter(email=transaction_base["email"]).count() == 1
