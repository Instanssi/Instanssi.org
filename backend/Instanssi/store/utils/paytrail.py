import hashlib
import hmac
import json
import logging
import uuid
from collections.abc import Mapping
from dataclasses import dataclass, fields
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Final, Iterable, Literal

import orjson
import requests
from yarl import URL

logger = logging.getLogger(__name__)

CREATE_PAYMENT_PATH: Final[str] = "/payments"


@dataclass
class Base:
    @staticmethod
    def format_key(data: str) -> str:
        chunks = data.split("_")
        out = [chunks[0]] if chunks else []
        for chunk in chunks[1:]:
            out.append(chunk.capitalize())
        return "".join(out)

    def format_value(self, v: Any) -> Any:
        if isinstance(v, Base):
            return v.to_dict()
        if isinstance(v, list):
            return [self.format_value(t) for t in v]
        if isinstance(v, datetime):
            return v.isoformat(timespec="milliseconds")
        if isinstance(v, Enum):
            return v.value
        if isinstance(v, URL):
            return str(v)
        return v

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for field in fields(self):
            key = field.name
            value = getattr(self, key)
            if value is not None:
                out[self.format_key(key)] = self.format_value(value)
        return out


@dataclass
class Item(Base):
    """Ref: https://docs.paytrail.com/#/?id=item"""

    unit_price: int
    units: int
    vat_percentage: int
    product_code: str
    description: str | None = None
    category: str | None = None
    orderId: str | None = None


@dataclass
class Customer(Base):
    """Ref: https://docs.paytrail.com/#/?id=customer-1"""

    email: str
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    vat_id: str | None = None
    company_name: str | None = None


@dataclass
class Address(Base):
    """Ref: https://docs.paytrail.com/#/?id=address"""

    street_address: str
    postal_code: str
    city: str
    country: str
    county: str | None = None


@dataclass
class CallbackUrl(Base):
    """Ref: https://docs.paytrail.com/#/?id=callbackurl"""

    success: URL
    cancel: URL


@dataclass
class Payment(Base):
    """Ref: https://docs.paytrail.com/#/?id=request-body"""

    stamp: str
    reference: str
    amount: int
    currency: Literal["EUR"]
    language: Literal["FI", "EN", "SV"]
    items: list[Item]
    customer: Customer
    redirect_urls: CallbackUrl
    callback_urls: CallbackUrl | None = None
    delivery_address: Address | None = None
    invoicing_address: Address | None = None


@dataclass
class NewPaymentResponse(Base):
    """Ref: https://docs.paytrail.com/#/?id=response"""

    href: str
    transaction_id: str
    request_id: str


class NewPaymentStatus(Enum):
    """Ref: https://docs.paytrail.com/#/?id=statuses"""

    NEW = "new"
    OK = "ok"
    FAIL = "fail"
    PENDING = "pending"
    DELAYED = "delayed"


@dataclass
class NewPaymentCallback(Base):
    """Ref: https://docs.paytrail.com/#/?id=redirect-and-callback-url-parameters"""

    account: str
    algorithm: str
    amount: int
    stamp: str
    reference: str
    transaction_id: str
    status: NewPaymentStatus
    provider: str

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "NewPaymentCallback":
        raw = {k[9:].replace("-", "_"): v for k, v in data.items() if k.startswith("checkout-")}
        return cls(
            amount=int(raw.pop("amount")),
            status=NewPaymentStatus(raw.pop("status")),
            **raw,
        )


class RequestMethod(Enum):
    GET = "GET"
    POST = "POST"


class PaymentMethod(Enum):
    MOBILE = "mobile"
    BANK = "bank"
    CREDIT_CARD = "creditcard"
    CREDIT = "credit"
    OTHER = "other"


class HashMethod(Enum):
    SHA256 = "sha256"
    SHA512 = "sha512"

    @classmethod
    def options(cls) -> list[str]:
        return [v.value for v in cls]


HASH_METHODS: dict[HashMethod, Any] = {
    HashMethod.SHA256: hashlib.sha256,
    HashMethod.SHA512: hashlib.sha512,
}


class PaytrailError(Exception):
    pass


class PaytrailRequestError(PaytrailError):
    pass


class PaytrailResponseError(PaytrailError):
    pass


def generate_hmac_sha(secret: str, message: bytes, hash_method: HashMethod) -> str:
    """Generates HMAC hash with SHA-512 or SHA-256"""
    return hmac.new(key=secret.encode(), msg=message, digestmod=HASH_METHODS[hash_method]).hexdigest()


def generate_payment_headers(
    account: str,
    method: RequestMethod,
    transaction_id: str | None = None,
    hash_method: HashMethod = HashMethod.SHA256,
) -> dict[str, str]:
    """Generates payment headers for HTTP requests."""
    headers = {
        "checkout-account": account,
        "checkout-algorithm": hash_method.value,
        "checkout-method": method.value,
        "checkout-nonce": str(uuid.uuid4()),
        "checkout-timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
    }
    if transaction_id:
        headers["checkout-transaction-id"] = transaction_id
    return headers


def generate_hmac_signature(
    secret: str, params: Mapping[str, str], body: bytes = b"", hash_method: HashMethod = HashMethod.SHA256
) -> str:
    """
    Grab all checkout headers from dict, sort them out and generate a valid HMAC signature
    for them. If body is given, it is used as a part of the message. This is required
    hashing method by Paytrail.

    Args:
        secret: Secret we use for signing
        params: Parameters to hash
        body: Body element to hash (optional)
        hash_method: Algorithm to use (defaults to sha-512)

    Returns:
        Signature hex string
    """
    checkout_headers = {k: v for k, v in params.items() if k.startswith("checkout-")}
    packed = [f"{k}:{v}".encode() for k, v in sorted(checkout_headers.items())]
    packed.append(body)
    return generate_hmac_sha(secret, b"\n".join(packed), hash_method)


def verify_signature(params: Mapping[str, str], body: bytes, secret: str) -> None:
    """Verifies paytrail api response signature HMAC hash"""
    signature_header = params.get("signature")
    algorithm_header = params.get("checkout-algorithm")

    if not signature_header:
        raise PaytrailResponseError("Invalid response; missing HMAC signature header")
    if not algorithm_header or algorithm_header not in HashMethod.options():
        raise PaytrailResponseError("Invalid response; missing or invalid algorithm header")

    expected = generate_hmac_signature(secret, params, body, HashMethod(algorithm_header))
    if expected != signature_header:
        raise PaytrailResponseError("Invalid response; signature mismatch")


def verify_account(params: Mapping[str, str], account: str) -> None:
    """Verify account id parameter"""
    account_param = params.get("checkout-account")
    if not account_param:
        raise PaytrailResponseError("Invalid response; missing account argument")
    if account_param != account:
        raise PaytrailResponseError(f"Invalid response; unexpected account argument value '{account_param}'")


def verify_method(params: Mapping[str, str], method: RequestMethod) -> None:
    """Verify checkout method parameter"""
    method_param = params.get("checkout-method")
    if not method_param:
        raise PaytrailResponseError("Invalid response; missing method argument")
    if method_param != method.value:
        raise PaytrailResponseError(f"Invalid response; unexpected method argument value '{method_param}'")


def _parse_response(body: str) -> Any:
    try:
        return json.loads(body)
    except json.JSONDecodeError as e:
        raise PaytrailRequestError("Error while parsing response data") from e


def decode_error_message(response: requests.Response) -> str:
    """Attempt to decode paytrail error message"""
    try:
        result: str = json.loads(response.content)["message"]
        return result
    except (json.JSONDecodeError, KeyError):
        return "<no message>"


def make_request(
    method: RequestMethod,
    address: URL,
    params: dict[str, str],
    account: str,
    secret: str,
    body: dict[str, Any] | list[Any] | None = None,
    hash_method: HashMethod = HashMethod.SHA256,
) -> tuple[Any, str]:
    """
    Make a HTTP request to the API. Authentication headers, signature and response
    verification is handled all here.

    Args:
        method: Request method (GET or POST)
        address: API entrypoint address
        params: Possible url parameters (?something=x)
        account: Account username
        secret: Account password
        body: List or Dict body element (None if empty)
        hash_method: Hash method to use for signature (Defaults to SHA256)

    Returns:
        JSON response, content depends on entrypoint.
    """
    encoded_body: bytes = orjson.dumps(body) if body is not None else b""
    payment_headers = generate_payment_headers(account, method, hash_method=hash_method)
    signature_hash = generate_hmac_signature(secret, payment_headers, encoded_body, hash_method)
    headers = {
        **payment_headers,
        "signature": signature_hash,
        "Content-Type": "application/json; charset=utf-8",
        "Connection": "close",
    }

    try:
        response = requests.request(
            method.value, str(address), headers=headers, params=params, data=encoded_body
        )
        response.raise_for_status()
        response_data = response.content
    except UnicodeDecodeError as e:
        raise PaytrailRequestError("Error while decoding response data") from e
    except requests.exceptions.RequestException as e:
        msg = decode_error_message(e.response) if e.response is not None else "<no response>"
        raise PaytrailRequestError(f"Paytrail request failed: {msg}") from e

    verify_account(params=response.headers, account=account)
    verify_method(params=response.headers, method=method)
    verify_signature(params=response.headers, body=response_data, secret=secret)
    return _parse_response(response_data.decode()), response.headers.get("request-id", "")


def create_payment(
    base_url: URL,
    account: str,
    secret: str,
    payment: Payment,
    amount: int | None = None,
    groups: Iterable[PaymentMethod] | None = None,
) -> NewPaymentResponse:
    """
    Initiates a payment to Paytrail. For request & response field docs,
    see paytrail docs @ https://docs.paytrail.com/#/?id=create

    Args:
        base_url: Base paytrail API URL
        account: Merchant ID (username)
        secret: Merchant secret (password)
        payment: Filled payment object
        amount: Cost of the payment in minor units (cents). Some payment methods have limits.
        groups: Groups of payment methods we wish to receive (eg. PaymentMethod.BANK)

    Returns:
        NewPaymentResponse object
    """
    address = base_url.with_path(CREATE_PAYMENT_PATH)
    params = {}
    if amount is not None:
        params["amount"] = str(amount)
    if groups is not None:
        params["groups"] = ",".join([g.value for g in groups])
    response, request_id = make_request(
        RequestMethod.POST, address, params, account, secret, body=payment.to_dict()
    )
    return NewPaymentResponse(
        href=response["href"], transaction_id=response["transactionId"], request_id=request_id
    )


def verify_callback(
    params: dict[str, str],
    account: str,
    secret: str,
) -> NewPaymentCallback:
    """
    Verifies a callback that Paytrail has made towards us. Params field should contain the GET parameters that
    were received. We will make sure that the signature is a match, and then parse and return the data nicely
    wrapped up.

    Args:
        params: GET parameters received from the request
        account: Merchant ID (username)
        secret: Merchant secret (password)

    Returns:
        NewPaymentCallback object
    """
    verify_signature(params=params, body=b"", secret=secret)
    verify_account(params=params, account=account)
    return NewPaymentCallback.from_dict(params)
