import hashlib
from typing import Dict
from urllib.parse import urlencode
from uuid import uuid4

import pytest
import requests_mock
from django.conf import settings
from django.core import mail
from django.test import RequestFactory
from django.urls import reverse

from Instanssi.store.handlers import begin_payment_process
from Instanssi.store.methods import PaymentMethod
from Instanssi.store.models import Receipt, StoreTransaction


def form_query(view_name: str, query: Dict[str, str], **kwargs) -> str:
    """Easy way to make paths with query strings"""
    url = reverse(view_name, kwargs=kwargs)
    if query:
        return "{}?{}".format(url, urlencode(query))
    return url


def make_success_auth_code(order_no: str, timestamp: str, paid: str, method: str) -> str:
    """
    This generates a paytrail success code. Success code is used as a check sum
    for verifying success events by paytrail.
    """
    m = hashlib.md5()
    m.update(
        "{}|{}|{}|{}|{}".format(order_no, timestamp, paid, method, settings.PAYTRAIL_SECRET).encode("UTF-8")
    )
    return m.hexdigest().upper()


def make_fail_auth_code(order_no: str, timestamp: str) -> str:
    """
    This generates a paytrail failure auth code. Fail code is used as a check
    sum for verifying failure events by paytrail.
    """
    m = hashlib.md5()
    m.update("{}|{}|{}".format(order_no, timestamp, settings.PAYTRAIL_SECRET).encode("UTF-8"))
    return m.hexdigest().upper()


@pytest.mark.django_db
def test_paytrail_begin_payment_process_bad_request(new_transaction):
    """Make sure paytrail fails properly (we should get a failure redirect url)"""
    request = RequestFactory().get("/")

    # Respond to paytrail calls with 401 error.
    with requests_mock.Mocker() as m:
        m.get(
            settings.PAYTRAIL_API_URL,
            status_code=401,
            json={"errorMessage": "Testing failure", "errorCode": "401"},
        )
        result = begin_payment_process(request, PaymentMethod.PAYTRAIL, new_transaction)

    assert result == reverse("store:pm:paytrail-failure")
    assert new_transaction.token == ""


@pytest.mark.django_db
def test_paytrail_begin_payment_process_good_request(
    new_transaction: StoreTransaction,
    new_transaction_item,
    new_transaction_item_copy,
    new_transaction_item3,
    new_transaction_item4,
    new_transaction_item2,
):
    """Make sure paytrail works with a good request (we should get a redirect URL)"""
    request = RequestFactory().get("/")
    token = uuid4().hex

    with requests_mock.Mocker() as m:
        m.post(
            settings.PAYTRAIL_API_URL,
            status_code=201,
            json={
                "orderNumber": "234246654",
                "token": token,
                "url": f"https://localhost/payment/load/token/{token}",
            },
        )
        result = begin_payment_process(request, PaymentMethod.PAYTRAIL, new_transaction)

        assert m.called_once
        assert m.last_request.json() == {
            "currency": "EUR",
            "locale": "fi_FI",
            "orderDetails": {
                "contact": {
                    "address": {
                        "country": new_transaction.country.code,
                        "postalCode": new_transaction.postalcode,
                        "postalOffice": new_transaction.city,
                        "street": new_transaction.street,
                    },
                    "companyName": new_transaction.company,
                    "email": new_transaction.email,
                    "firstName": new_transaction.firstname,
                    "lastName": new_transaction.lastname,
                    "mobile": new_transaction.mobile,
                    "telephone": new_transaction.telephone,
                },
                "includeVat": 1,
                "products": [
                    {
                        "amount": "1",
                        "code": "3",
                        "price": "20.00",
                        "title": "Secret item",
                        "type": 1,
                        "vat": "0",
                    },
                    {
                        "amount": "1",
                        "code": "2",
                        "price": "20.00",
                        "title": "Test item 1",
                        "type": 1,
                        "vat": "0",
                    },
                    {
                        "amount": "1",
                        "code": "1:2",
                        "price": "20.00",
                        "title": "Test item 1, S",
                        "type": 1,
                        "vat": "0",
                    },
                    {
                        "amount": "2",
                        "code": "1:1",
                        "price": "20.00",
                        "title": "Test item 1, XXL",
                        "type": 1,
                        "vat": "0",
                    },
                ],
            },
            "orderNumber": "1",
            "urlSet": {
                "failure": "http://testserver/store/pm/paytrail/failure/",
                "notification": "http://testserver/store/pm/paytrail/notify/",
                "pending": "",
                "success": "http://testserver/store/pm/paytrail/success/",
            },
        }

    # Verify the result
    assert result == f"https://localhost/payment/load/token/{token}"

    # Make sure database has the token and payment method now
    # Also, date-times should also be unset
    new_transaction.refresh_from_db()
    assert new_transaction.token == token
    assert new_transaction.payment_method_name == "Paytrail"
    assert new_transaction.time_paid is None
    assert new_transaction.time_cancelled is None
    assert new_transaction.time_pending is None


@pytest.mark.django_db
def test_paytrail_success_endpoint_validates(new_transaction, page_client):
    # Set the transaction to started state
    new_transaction.token = uuid4().hex
    new_transaction.payment_method_name = "Paytrail"
    new_transaction.save()

    # Then attempt to call the success notification entrypoint.
    # Normally paytrail API does this.
    url = form_query(
        "store:pm:paytrail-success",
        query={
            "ORDER_NUMBER": str(new_transaction.id),
            "TIMESTAMP": "0",
            "PAID": "asd",
            "METHOD": "2",
            "RETURN_AUTHCODE": make_success_auth_code(new_transaction.id, "0", "asd", "2"),
        },
    )
    result = page_client.get(url)

    # On our end, the success handler has validate the payment as done, and
    # does a redirect to clean up the browsers address line.
    assert result.status_code == 302
    assert result.url == reverse("store:pm:paytrail-success")

    # Check that database was updated with state
    new_transaction.refresh_from_db()
    assert new_transaction.time_paid is None
    assert new_transaction.time_cancelled is None
    assert new_transaction.time_pending is not None  # Should be pending!

    # Ensure receipt was not yet created and mail was not yet sent
    assert Receipt.objects.filter(mail_to=new_transaction.email).count() == 0
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_paytrail_success_endpoint_does_not_validate(new_transaction, page_client):
    # Set the transaction to started state
    new_transaction.token = uuid4().hex
    new_transaction.payment_method_name = "Paytrail"
    new_transaction.save()

    # Then attempt to call the success notification entrypoint.
    # Normally paytrail API does this.
    url = form_query(
        "store:pm:paytrail-success",
        query={
            "ORDER_NUMBER": str(new_transaction.id),
            "TIMESTAMP": "0",
            "PAID": "asd",
            "METHOD": "2",
            "RETURN_AUTHCODE": "",  # Incorrect hash
        },
    )
    result = page_client.get(url)

    # On our end, the success handler was not able to validate the transaction
    # as completed. We remain waiting for completion signal, and just show the
    # success message for now.
    assert result.status_code == 200
    assert "store/success.html" in {tpl.name for tpl in result.templates}

    # Check that database was NOT updated (no valid paytrail query)
    new_transaction.refresh_from_db()
    assert new_transaction.time_paid is None
    assert new_transaction.time_cancelled is None
    assert new_transaction.time_pending is None

    # Ensure receipt was NOT created and mail was NOT sent
    assert Receipt.objects.filter(mail_to=new_transaction.email).count() == 0
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_paytrail_notify_endpoint_ok(page_client, new_transaction):
    # Set the transaction to started state
    new_transaction.token = uuid4().hex
    new_transaction.payment_method_name = "Paytrail"
    new_transaction.save()

    # Then attempt to call the success notification entrypoint.
    # Normally paytrail API does this.
    url = form_query(
        "store:pm:paytrail-notify",
        query={
            "ORDER_NUMBER": str(new_transaction.id),
            "TIMESTAMP": "0",
            "PAID": "asd",
            "METHOD": "2",
            "RETURN_AUTHCODE": make_success_auth_code(new_transaction.id, "0", "asd", "2"),
        },
    )
    result = page_client.get(url)
    assert result.status_code == 200
    assert result.content == b""

    # Check that database was updated with state
    new_transaction.refresh_from_db()
    assert new_transaction.time_paid is not None
    assert new_transaction.time_cancelled is None
    assert new_transaction.time_pending is not None

    # Ensure receipt was created and mail was sent
    assert Receipt.objects.get(mail_to=new_transaction.email)
    assert len(mail.outbox) == 1


@pytest.mark.django_db
def test_paytrail_failure_endpoint_validates(page_client, new_transaction):
    # Set the transaction to started state
    new_transaction.token = uuid4().hex
    new_transaction.payment_method_name = "Paytrail"
    new_transaction.save()

    # Then attempt to call the success notification entrypoint.
    # Normally paytrail API does this.
    url = form_query(
        "store:pm:paytrail-failure",
        query={
            "ORDER_NUMBER": str(new_transaction.id),
            "TIMESTAMP": "0",
            "RETURN_AUTHCODE": make_fail_auth_code(new_transaction.id, "0"),
        },
    )
    result = page_client.get(url)

    # On our end, the error handler has validate the payment as failed, and
    # does a redirect to clean up the browsers address line.
    assert result.status_code == 302
    assert result.url == reverse("store:pm:paytrail-failure")

    # Check that database was updated with state
    new_transaction.refresh_from_db()
    assert new_transaction.time_paid is None
    assert new_transaction.time_cancelled is not None  # Should be failed!
    assert new_transaction.time_pending is None

    # Ensure receipt was NOT created and mail was NOT sent
    assert Receipt.objects.filter(mail_to=new_transaction.email).count() == 0
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_paytrail_failure_endpoint_does_not_validate(page_client, new_transaction):
    # Set the transaction to started state
    new_transaction.token = uuid4().hex
    new_transaction.payment_method_name = "Paytrail"
    new_transaction.save()

    # Then attempt to call the success notification entrypoint.
    # Normally paytrail API does this.
    url = form_query(
        "store:pm:paytrail-failure",
        query={
            "ORDER_NUMBER": str(new_transaction.id),
            "TIMESTAMP": "0",
            "RETURN_AUTHCODE": "",  # Invalid hash code
        },
    )
    result = page_client.get(url)

    assert result.status_code == 200
    assert "store/failure.html" in {tpl.name for tpl in result.templates}

    # Check that database was NOT updated (no valid paytrail query)
    new_transaction.refresh_from_db()
    assert new_transaction.time_paid is None
    assert new_transaction.time_cancelled is None
    assert new_transaction.time_pending is None

    # Ensure receipt was NOT created and mail was NOT sent
    assert Receipt.objects.filter(mail_to=new_transaction.email).count() == 0
    assert len(mail.outbox) == 0
