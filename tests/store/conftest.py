from decimal import Decimal
from typing import Any, Callable, Dict
from uuid import uuid4

from django.urls import reverse
from django.utils import timezone
from pytest import fixture

from Instanssi.store.models import (
    Receipt,
    StoreItem,
    StoreItemVariant,
    StoreTransaction,
)
from Instanssi.store.utils.receipt import ReceiptParams


@fixture
def base_store_item(faker, event, image_png) -> Callable[[], StoreItem]:
    def _inner() -> StoreItem:
        return StoreItem(
            name="Test item 1",
            event=event,
            description=faker.text(),
            price=Decimal("20.00"),
            max=50,
            available=True,
            max_per_order=5,
            sort_index=0,
            discount_amount=-1,
            discount_percentage=0,
            is_ticket=False,
            secret_key="",
            imagefile_original=image_png,
        )

    return _inner


@fixture
def store_item(base_store_item) -> StoreItem:
    store_item = base_store_item()
    store_item.save()
    return store_item


@fixture
def hidden_item(base_store_item) -> StoreItem:
    store_item = base_store_item()
    store_item.name = "Secret item"
    store_item.is_secret = True
    store_item.secret_key = "kissa"
    store_item.save(force_insert=True)
    return store_item


@fixture
def variant_item(base_store_item) -> StoreItem:
    store_item = base_store_item()
    store_item.save()
    return store_item


@fixture
def discount_item(base_store_item) -> StoreItem:
    store_item = base_store_item()
    store_item.discount_amount = 5
    store_item.discount_percentage = 50
    store_item.save()
    return store_item


@fixture
def store_item_variant(variant_item) -> StoreItemVariant:
    return StoreItemVariant.objects.create(item=variant_item, name="XXL")


@fixture
def store_item_variant2(variant_item) -> StoreItemVariant:
    return StoreItemVariant.objects.create(item=variant_item, name="S")


@fixture
def new_transaction(faker, event) -> StoreTransaction:
    return StoreTransaction.objects.create(
        time_created=timezone.now(),
        key=uuid4().hex,
        firstname=faker.first_name(),
        lastname=faker.last_name(),
        email=faker.email(),
        street=faker.street_address(),
        postalcode=faker.postcode(),
        city=faker.city(),
        information=faker.text(),
    )


@fixture
def receipt_params(faker) -> ReceiptParams:
    p = ReceiptParams()
    p.order_number(20000)
    p.receipt_number(1000)
    p.receipt_date(timezone.now())
    p.order_date(timezone.now())
    p.first_name(faker.first_name())
    p.last_name(faker.last_name())
    p.email(faker.email())
    p.mobile(faker.phone_number())
    p.telephone(faker.phone_number())
    p.company(faker.company())
    p.street(faker.street_address())
    p.city(faker.city())
    p.postal_code(faker.postcode())
    p.country(faker.country_code())
    p.transaction_url(reverse("store:ta_view", args=("1234abcd",)))
    for k in range(3):
        p.add_item(
            item_id=1000 + k,
            price=Decimal(k),
            name=f"Test product {k}",
            amount=k,
            tax="0%",
        )
    return p


@fixture
def json_receipt_params(receipt_params) -> dict:
    params = receipt_params.params
    output = {
        "order_number": params["order_number"],
        "receipt_number": params["receipt_number"],
        "receipt_date": params["receipt_date"].isoformat(),
        "order_date": params["order_date"].isoformat(),
        "first_name": params["first_name"],
        "last_name": params["last_name"],
        "mobile": params["mobile"],
        "email": params["email"],
        "telephone": params["telephone"],
        "company": params["company"],
        "street": params["street"],
        "city": params["city"],
        "postal_code": params["postal_code"],
        "country": params["country"],
        "items": [],
        "transaction_url": params["transaction_url"],
        "total": str(params["total"]),
    }
    for item in params["items"]:
        output["items"].append(
            {
                "id": item["id"],
                "name": item["name"],
                "price": str(item["price"]),
                "amount": item["amount"],
                "total": str(item["total"]),
                "tax": item["tax"],
            }
        )
    return output


@fixture
def receipt(receipt_params) -> Receipt:
    return Receipt.create(
        mail_to=receipt_params.params["email"],
        mail_from="Instanssi.org <noreply@instanssi.org>",
        subject="Test email",
        params=receipt_params,
    )


@fixture
def transaction_base() -> Dict[str, Any]:
    """Common base for creating new transactions via create_store_transaction()"""
    return {
        "first_name": "Donald",
        "last_name": "Duck",
        "company": "Duck Co",
        "email": "donald.duck@duckburg.inv",
        "telephone": "991234567",
        "mobile": "+358991234567",
        "street": "1313 Webfoot Walk",
        "postal_code": "00000",
        "city": "Duckburg",
        "country": "US",
        "information": "Quack, damn you!",
        "items": [],
    }
