from copy import copy
from decimal import Decimal
from unittest import mock
from unittest.mock import ANY
from uuid import uuid4

import pytest
from django.core import mail
from django.test import override_settings
from django.test.client import RequestFactory
from django.urls import reverse
from yarl import URL

from Instanssi.store.methods.paytrail import start_process
from Instanssi.store.models import StoreTransaction, StoreTransactionEvent
from Instanssi.store.utils.paytrail import (
    Address,
    CallbackUrl,
    Customer,
    Item,
    NewPaymentResponse,
    NewPaymentStatus,
    Payment,
    PaymentMethod,
)


def test_paytrail_success_endpoint(page_client):
    url = reverse("store:pm:paytrail-success")
    result = page_client.get(url)
    assert result.status_code == 200
    assert "store/success.html" in {tpl.name for tpl in result.templates}


def test_paytrail_cancel_endpoint(page_client):
    url = reverse("store:pm:paytrail-cancel")
    result = page_client.get(url)
    assert result.status_code == 200
    assert "store/failure.html" in {tpl.name for tpl in result.templates}


@pytest.mark.django_db
def test_paytrail_redirect_success_endpoint(page_client, paytrail_callback_params, account, secret):
    url = reverse("store:pm:paytrail-redirect-success")
    with override_settings(PAYTRAIL_V2_ID=account, PAYTRAIL_V2_SECRET=secret):
        result = page_client.get(url, paytrail_callback_params)
        assert result.status_code == 302
        assert result.url == reverse("store:pm:paytrail-success")


@pytest.mark.django_db
def test_paytrail_redirect_cancel_endpoint(page_client, paytrail_callback_params, account, secret):
    url = reverse("store:pm:paytrail-redirect-cancel")
    with override_settings(PAYTRAIL_V2_ID=account, PAYTRAIL_V2_SECRET=secret):
        result = page_client.get(url, paytrail_callback_params)
        assert result.status_code == 302
        assert result.url == reverse("store:pm:paytrail-cancel")


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
@pytest.mark.django_db
def test_paytrail_callback_endpoint_ok(page_client, callback_generator, account, secret, store_transaction):
    store_transaction.time_paid = None
    store_transaction.save()

    url = reverse("store:pm:paytrail-callback")
    params = callback_generator(NewPaymentStatus.OK)
    with override_settings(PAYTRAIL_V2_ID=account, PAYTRAIL_V2_SECRET=secret):
        result = page_client.get(url, params)
        assert result.status_code == 200
        assert result.content == b"{}"

    events = StoreTransactionEvent.objects.all()
    assert events.count() == 2

    # This is the callback event
    assert events[0].data == {
        "account": "test-account",
        "algorithm": "sha256",
        "amount": 1000,
        "provider": "some-back",
        "reference": "1",
        "stamp": "1",
        "status": "ok",
        "transactionId": "7f17f6d8-7b39-11ed-8278-439349c0f5fa",
    }
    assert events[0].transaction == store_transaction
    assert events[0].message == "Callback"
    assert events[0].created is not None

    # This is the mail sending event
    assert events[1].data == {"mail_to": ANY, "receipt_id": ANY}
    assert events[1].transaction == store_transaction
    assert events[1].message == "Receipt sent"
    assert events[1].created is not None

    # Make sure mail was handled
    assert len(mail.outbox) == 1

    # Ensure the transaction was marked properly
    store_transaction.refresh_from_db()
    assert store_transaction.time_paid is not None
    assert store_transaction.is_paid is True


@pytest.mark.django_db
def test_paytrail_callback_endpoint_fail(
    page_client, callback_generator, account, secret, store_transaction
):
    store_transaction.time_cancelled = None
    store_transaction.save()

    url = reverse("store:pm:paytrail-callback")
    params = callback_generator(NewPaymentStatus.FAIL)
    with override_settings(PAYTRAIL_V2_ID=account, PAYTRAIL_V2_SECRET=secret):
        result = page_client.get(url, params)
        assert result.status_code == 200
        assert result.content == b"{}"

    events = StoreTransactionEvent.objects.all()
    assert events.count() == 1

    assert events[0].data == {
        "account": "test-account",
        "algorithm": "sha256",
        "amount": 1000,
        "provider": "some-back",
        "reference": "1",
        "stamp": "1",
        "status": "fail",
        "transactionId": "7f17f6d8-7b39-11ed-8278-439349c0f5fa",
    }
    assert events[0].transaction == store_transaction
    assert events[0].message == "Callback"
    assert events[0].created is not None

    # Pending time should now be set
    store_transaction.refresh_from_db()
    assert store_transaction.time_cancelled is not None
    assert store_transaction.is_cancelled is True


@pytest.mark.django_db
def test_paytrail_callback_endpoint_pending(
    page_client, callback_generator, account, secret, store_transaction
):
    store_transaction.time_pending = None
    store_transaction.save()

    url = reverse("store:pm:paytrail-callback")
    params = callback_generator(NewPaymentStatus.PENDING)
    with override_settings(PAYTRAIL_V2_ID=account, PAYTRAIL_V2_SECRET=secret):
        result = page_client.get(url, params)
        assert result.status_code == 200
        assert result.content == b"{}"

    events = StoreTransactionEvent.objects.all()
    assert events.count() == 1

    assert events[0].data == {
        "account": "test-account",
        "algorithm": "sha256",
        "amount": 1000,
        "provider": "some-back",
        "reference": "1",
        "stamp": "1",
        "status": "pending",
        "transactionId": "7f17f6d8-7b39-11ed-8278-439349c0f5fa",
    }
    assert events[0].transaction == store_transaction
    assert events[0].message == "Callback"
    assert events[0].created is not None

    # Pending time should now be set
    store_transaction.refresh_from_db()
    assert store_transaction.time_pending is not None
    assert store_transaction.is_pending is True


@pytest.mark.django_db
def test_start_process(
    store_transaction, transaction_item_generator, store_item, variant_item, store_item_variant
):
    request_factory = RequestFactory()

    # These are the same, so they generate one Item with amount = 2
    item_a_1 = transaction_item_generator(store_item)
    item_a_2 = transaction_item_generator(store_item)

    # This is the same item as above, but different price, so it is a different line item in the order
    item_b = transaction_item_generator(store_item, price=Decimal("24.00"))

    # Completely separate item with an item variant
    item_c = transaction_item_generator(variant_item, variant=store_item_variant)

    with mock.patch("Instanssi.store.methods.paytrail.create_payment") as fn:
        fn.return_value = NewPaymentResponse(
            href="http://localhost", request_id="request-id", transaction_id="new-transaction-id"
        )
        data = start_process(request_factory.post("/some/path"), store_transaction)
        assert data == "http://localhost"

        # Check the data we sent to paytrail
        fn.assert_called_once_with(
            URL("http://localhost:8000"),
            "",
            "",
            Payment(
                stamp=str(store_transaction.id),
                reference=str(store_transaction.id),
                amount=2700,
                currency="EUR",
                language="FI",
                items=[
                    Item(
                        unit_price=100,
                        units=2,
                        vat_percentage=0,
                        product_code="1",
                        description="Test item 1",
                    ),
                    Item(
                        unit_price=2400,
                        units=1,
                        vat_percentage=0,
                        product_code="1",
                        description="Test item 1",
                    ),
                    Item(
                        unit_price=100,
                        units=1,
                        vat_percentage=0,
                        product_code="2:1",
                        description="Test item 1, XXL",
                    ),
                ],
                customer=Customer(
                    email=store_transaction.email,
                    first_name=store_transaction.firstname,
                    last_name=store_transaction.lastname,
                    phone=store_transaction.telephone,
                    company_name=store_transaction.company,
                ),
                redirect_urls=CallbackUrl(
                    success=URL("http://testserver/store/pm/paytrail/redirect/success/"),
                    cancel=URL("http://testserver/store/pm/paytrail/redirect/cancel/"),
                ),
                callback_urls=CallbackUrl(
                    success=URL("http://testserver/store/pm/paytrail/callback/"),
                    cancel=URL("http://testserver/store/pm/paytrail/callback/"),
                ),
                invoicing_address=Address(
                    street_address=store_transaction.street,
                    postal_code=store_transaction.postalcode,
                    city=store_transaction.city,
                    country=store_transaction.country.code,
                ),
            ),
            groups=[PaymentMethod.BANK],
        )

    # Make sure state was saved
    store_transaction.refresh_from_db()
    assert store_transaction.token == "new-transaction-id"
    assert store_transaction.payment_method_name == "Paytrail"
