import hmac
from datetime import datetime, timezone
from unittest.mock import patch
from uuid import uuid4

import freezegun
from pytest import fixture
from yarl import URL

from Instanssi.store.utils.paytrail import (
    CallbackUrl,
    Customer,
    Item,
    NewPaymentStatus,
    Payment,
    PaymentMethod,
)


@fixture
def account():
    return "test-account"


@fixture
def secret():
    return "test-secret"


@fixture
def amount():
    return 1500


@fixture
def timestamp():
    ts = datetime(2022, 12, 10, 19, 44, 56, 179011, tzinfo=timezone.utc)
    with freezegun.freeze_time(ts):
        yield ts


@fixture
def nonce():
    value = uuid4()
    with patch("Instanssi.store.utils.paytrail.uuid.uuid4") as fn:
        fn.return_value = value
        yield value


@fixture
def groups():
    return [PaymentMethod.BANK, PaymentMethod.MOBILE]


@fixture
def paytrail_callback_params(account, store_transaction):
    return {
        "checkout-account": account,
        "checkout-algorithm": "sha256",
        "checkout-amount": "1000",
        "checkout-stamp": str(store_transaction.id),
        "checkout-reference": str(store_transaction.id),
        "checkout-status": "ok",
        "checkout-provider": "some-back",
        "checkout-transaction-id": "7f17f6d8-7b39-11ed-8278-439349c0f5fa",
        "signature": "7088d83fc8a929c19ea54c707fb6007703c03e9bdd13a7f8678a53a90f08fccc",
    }


@fixture
def callback_generator(account, secret, store_transaction):
    """Generates valid looking callback parameters"""

    def _generator(status: NewPaymentStatus):
        params = {
            "checkout-account": account,
            "checkout-algorithm": "sha256",
            "checkout-amount": "1000",
            "checkout-stamp": str(store_transaction.id),
            "checkout-reference": str(store_transaction.id),
            "checkout-status": status.value,
            "checkout-provider": "some-back",
            "checkout-transaction-id": "7f17f6d8-7b39-11ed-8278-439349c0f5fa",
        }
        packed = [f"{k}:{v}" for k, v in sorted(params.items())] + [""]
        params["signature"] = hmac.new(
            key=secret.encode(), msg="\n".join(packed).encode(), digestmod="sha256"
        ).hexdigest()
        return params

    return _generator


@fixture
def paytrail_response_body():
    return {
        "transactionId": "2f5b7e1d-837b-49c7-8ad5-eb2e9514a9db",
        "href": "https://localhost/pay/2f5b7e1d-837b-49c7-8ad5-eb2e9514a9db",
        "reference": "809759248",
        "terms": "You agree to everything!",
        "groups": [],
        "providers": [],
        "customProviders": {},
    }


@fixture
def paytrail_response_headers(account):
    return {
        "Content-Type": "application/json; charset=utf-8",
        "checkout-account": account,
        "checkout-method": "POST",
        "checkout-algorithm": "sha256",
        "signature": "d6c86a887d1fca31e583834f64f058d8a8d09a50b37059da72ee316b6e90a251",
        "request-id": "b1436eaf-1ef7-4b5b-84c8-28b52c16521a",
    }


@fixture
def payment():
    return Payment(
        amount=1000,
        currency="EUR",
        language="FI",
        reference="1",
        stamp="1",
        callback_urls=CallbackUrl(
            success=URL("https://localhost/test/success/callback/"),
            cancel=URL("https://localhost/test/cancel/callback/"),
        ),
        redirect_urls=CallbackUrl(
            success=URL("https://localhost/test/success/redirect/"),
            cancel=URL("https://localhost/test/cancel/redirect/"),
        ),
        customer=Customer(
            first_name="Timo",
            last_name="Testaaja",
            email="timo.testaaja@invalid.inv",
        ),
        items=[Item(product_code="efsef34hf", unit_price=1000, units=1, vat_percentage=0)],
    )
