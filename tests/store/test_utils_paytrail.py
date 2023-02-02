import json
from unittest.mock import ANY

import pytest
import requests_mock
import yarl

from Instanssi.store.utils.paytrail import (
    CREATE_PAYMENT_PATH,
    HashMethod,
    NewPaymentCallback,
    NewPaymentStatus,
    PaymentMethod,
    PaytrailResponseError,
    RequestMethod,
    create_payment,
    generate_hmac_sha,
    generate_hmac_signature,
    generate_payment_headers,
    verify_account,
    verify_callback,
    verify_method,
    verify_signature,
)


def test_generate_hmac_sha512():
    out = generate_hmac_sha("secret", "message", HashMethod.SHA512)
    assert out == (
        "1bba587c730eedba31f53abb0b6ca589"
        "e09de4e894ee455e6140807399759ada"
        "afa069eec7c01647bb173dcb17f55d22"
        "af49a18071b748c5c2edd7f7a829c632"
    )


def test_generate_hmac_sha256():
    out = generate_hmac_sha("secret", "message", HashMethod.SHA256)
    assert out == "8b5f48702995c1598c573db1e21866a9b825d4a794d169d7060a03605796360b"


def test_generate_payment_headers(nonce, timestamp):
    out = generate_payment_headers("account", RequestMethod.GET, "transaction-id")
    assert out == {
        "checkout-account": "account",
        "checkout-algorithm": "sha256",
        "checkout-method": "GET",
        "checkout-nonce": str(nonce),
        "checkout-timestamp": timestamp.isoformat(timespec="milliseconds"),
        "checkout-transaction-id": "transaction-id",
    }


def test_generate_hmac_signature_no_headers():
    signature = generate_hmac_signature("secret", dict(), "message")
    assert signature == "8b5f48702995c1598c573db1e21866a9b825d4a794d169d7060a03605796360b"


def test_generate_hmac_signature_with_skipped_headers():
    signature = generate_hmac_signature("secret", {"test": "test"}, "message")
    assert signature == "8b5f48702995c1598c573db1e21866a9b825d4a794d169d7060a03605796360b"


def test_generate_hmac_signature_with_proper_headers():
    signature = generate_hmac_signature("secret", {"checkout-test": "test"}, "message")
    assert signature == "d037ddb2a4b602289dab92a62b6f3026faaad2e155108719f6cc07c5fca83b4e"


@pytest.mark.django_db
def test_verify_callback_ok(paytrail_callback_params, account, secret):
    out = verify_callback(paytrail_callback_params, account, secret)
    assert out == NewPaymentCallback(
        account="test-account",
        algorithm="sha256",
        amount=1000,
        stamp="1",
        reference="1",
        transaction_id="7f17f6d8-7b39-11ed-8278-439349c0f5fa",
        status=NewPaymentStatus.OK,
        provider="some-back",
    )


def test_verify_method_ok(paytrail_response_headers):
    verify_method(paytrail_response_headers, RequestMethod.POST)


def test_verify_account_ok(paytrail_response_headers, account):
    verify_account(paytrail_response_headers, account)


def test_verify_method_fail_method_wrong(paytrail_response_headers):
    with pytest.raises(
        PaytrailResponseError, match="Invalid response; unexpected method argument value 'POST'"
    ):
        verify_method(paytrail_response_headers, RequestMethod.GET)


def test_verify_method_fail_method_missing(paytrail_response_headers):
    paytrail_response_headers.pop("checkout-method")
    with pytest.raises(PaytrailResponseError, match="Invalid response; missing method argument"):
        verify_method(paytrail_response_headers, RequestMethod.GET)


def test_verify_account_fail_account_wrong(paytrail_response_headers):
    with pytest.raises(
        PaytrailResponseError, match="Invalid response; unexpected account argument value 'test-account'"
    ):
        verify_account(paytrail_response_headers, "wrong")


def test_verify_account_fail_account_missing(paytrail_response_headers, account):
    paytrail_response_headers.pop("checkout-account")
    with pytest.raises(PaytrailResponseError, match="Invalid response; missing account argument"):
        verify_account(paytrail_response_headers, account)


def test_verify_response_signature_ok(paytrail_response_headers, paytrail_response_body, secret):
    body = json.dumps(paytrail_response_body)
    verify_signature(paytrail_response_headers, body, secret)


def test_verify_response_signature_fail_mismatching_signature(paytrail_response_headers, secret):
    with pytest.raises(PaytrailResponseError, match="Invalid response; signature mismatch"):
        verify_signature(paytrail_response_headers, "wrong body", secret)


def test_verify_response_signature_fail_missing_signature(
    paytrail_response_headers, paytrail_response_body, secret
):
    paytrail_response_headers.pop("signature")
    with pytest.raises(PaytrailResponseError, match="Invalid response; missing HMAC signature header"):
        verify_signature(paytrail_response_headers, paytrail_response_body, secret)


def test_create_payment_response_ok(
    paytrail_response_body, paytrail_response_headers, account, secret, payment
):
    test_url = yarl.URL("http://localhost:8000")
    mock_url = test_url.with_path(CREATE_PAYMENT_PATH).with_query({"groups": "bank"})
    with requests_mock.Mocker() as m:
        m.post(
            str(mock_url), status_code=200, json=paytrail_response_body, headers=paytrail_response_headers
        )
        data = create_payment(test_url, account, secret, payment, groups=[PaymentMethod.BANK])

        assert data.transaction_id == "2f5b7e1d-837b-49c7-8ad5-eb2e9514a9db"
        assert data.href == "https://localhost/pay/2f5b7e1d-837b-49c7-8ad5-eb2e9514a9db"
        assert data.request_id == "b1436eaf-1ef7-4b5b-84c8-28b52c16521a"


def test_create_payment_request_ok(
    paytrail_response_body, paytrail_response_headers, account, secret, nonce, payment, timestamp
):
    test_url = yarl.URL("http://localhost:8000")
    mock_url = test_url.with_path(CREATE_PAYMENT_PATH).with_query({"groups": "bank"})
    with requests_mock.Mocker() as m:
        m.post(
            str(mock_url), status_code=200, json=paytrail_response_body, headers=paytrail_response_headers
        )
        create_payment(test_url, account, secret, payment, groups=[PaymentMethod.BANK])

        # Make sure our request looks correct
        assert m.last_request.headers == {
            # Set by requests
            "User-Agent": ANY,
            "Content-Length": ANY,
            "Accept-Encoding": ANY,
            "Accept": ANY,
            # Statically set by us
            "Content-Type": "application/json; charset=utf-8",
            "Connection": "close",
            # Paytrail stuff
            "checkout-account": "test-account",
            "checkout-algorithm": "sha256",
            "checkout-method": "POST",
            "checkout-nonce": str(nonce),
            "checkout-timestamp": timestamp.isoformat(timespec="milliseconds"),
            "signature": ANY,
        }

        assert json.loads(m.last_request.body) == {
            "amount": 1000,
            "callbackUrls": {
                "cancel": "https://localhost/test/cancel/callback/",
                "success": "https://localhost/test/success/callback/",
            },
            "currency": "EUR",
            "customer": {"email": "timo.testaaja@invalid.inv", "firstName": "Timo", "lastName": "Testaaja"},
            "items": [{"productCode": "efsef34hf", "unitPrice": 1000, "units": 1, "vatPercentage": 0}],
            "language": "FI",
            "redirectUrls": {
                "cancel": "https://localhost/test/cancel/redirect/",
                "success": "https://localhost/test/success/redirect/",
            },
            "reference": "1",
            "stamp": "1",
        }
