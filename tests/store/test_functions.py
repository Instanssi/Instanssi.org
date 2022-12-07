import json
from decimal import Decimal
from uuid import UUID

import arrow
import pytest
from django.conf import settings
from freezegun import freeze_time

from Instanssi.store.handlers import (
    TransactionException,
    create_store_transaction,
    validate_item,
    validate_payment_method,
)
from Instanssi.store.methods import PaymentMethod
from Instanssi.store.models import StoreItem, TransactionItem
from Instanssi.store.utils.receipt import ReceiptParams

FAKE_NOW = arrow.Arrow(year=2022, month=12, day=6, hour=10, timezone=settings.TIME_ZONE).datetime


@pytest.mark.django_db
def test_secret_items_no_password(hidden_item):
    """Test hiding secret items unless the correct key is provided."""
    assert list(StoreItem.items_visible()) == []
    assert list(StoreItem.items_visible("cat")) == []
    assert list(StoreItem.items_visible("kissa")) == [hidden_item]


def test_receipt_params_roundtrip(receipt_params):
    """Test receipt parameter json round-tripping"""
    n = ReceiptParams(receipt_params.get_json())
    assert n.params == receipt_params.params


@pytest.mark.django_db
@freeze_time(FAKE_NOW)
def test_create_receipt_fields_ok(receipt, receipt_params, json_receipt_params):
    """Test receipt creation (to database)"""
    receipt.refresh_from_db()
    assert receipt.subject == "Test email"
    assert receipt.mail_from == "Instanssi.org <noreply@instanssi.org>"
    assert receipt.mail_to == receipt_params.params["email"]
    assert receipt.content is not None
    assert json.loads(receipt.params) == json_receipt_params
    assert receipt.sent is None
    assert ReceiptParams(receipt.params).params == receipt_params.params


@pytest.mark.django_db
@freeze_time(FAKE_NOW)
def test_create_receipt_fields_sent_is_set(receipt):
    """Test receipt creation (to database)"""
    receipt.refresh_from_db()
    assert receipt.sent is None
    receipt.send()
    assert receipt.sent == FAKE_NOW


@pytest.mark.django_db
@freeze_time(FAKE_NOW)
def test_create_receipt_email_content(receipt, receipt_params):
    receipt.refresh_from_db()
    params = receipt_params.params
    order_date = arrow.get(params["order_date"]).to(settings.TIME_ZONE).datetime
    receipt_date = arrow.get(params["receipt_date"]).to(settings.TIME_ZONE).datetime
    assert receipt.content == (
        "Hei,\n"
        "\n"
        f"Tilauksenne numerolla {params['order_number']} on nyt käsitelty.\n"
        "\n"
        "Mikäli huomaatte virheitä tilausluettelossa, ottakaa yhteys meihin\n"
        "välittömästi (webmaster@instanssi.org). Ohessa seuraa tilausluettelo sekä\n"
        "linkki tuotteiden ja lippujen lunastukseen vaadittaviin tunnisteisiin.\n"
        "\n"
        "Huom! Tilauksen sisältämät tuotteet kuten T-paidat voi noutaa tapahtuman\n"
        "aikana lipunmyynnistä.\n"
        "\n"
        "Tilaajan tiedot:\n"
        "----------------\n"
        "\n"
        f"Nimi:          {params['first_name']} {params['last_name']}\n"
        f"Sähköposti:    {params['email']}\n"
        f"Yritys:        {params['company']}\n"
        f"Puhelinnumero: {params['telephone']}\n"
        f"Kännykkä:      {params['mobile']}\n"
        f"Katuosoite:    {params['street']}\n"
        f"Kaupunki:      {params['city']}\n"
        f"Postinumero:   {params['postal_code']}\n"
        f"Maakoodi:      {params['country']}\n"
        "\n"
        "Myyjän tiedot:\n"
        "--------------\n"
        "\n"
        "Linkki Jyväskylä ry (2147178-4)\n"
        "Agora, Ag C233.2, PL 35\n"
        "40014 Jyväskylän yliopisto\n"
        "\n"
        "Tilauksen tiedot:\n"
        "-----------------\n"
        "\n"
        f"Tilausnumero: {params['order_number']}\n"
        f"Tilausaika: {order_date.strftime('%d.%m.%Y %H:%M')}\n"
        f"Kuittinumero: {params['receipt_number']}\n"
        f"Kuitin toimitusaika: {receipt_date.strftime('%d.%m.%Y %H:%M')}\n"
        "\n"
        "  ID  Tuoteseloste      Hinta (€)    Määrä    Yhteensä (€)  Alv.\n"
        "----  --------------  -----------  -------  --------------  ------\n"
        "1000  Test product 0            0        0               0  0%\n"
        "1001  Test product 1            1        1               1  0%\n"
        "1002  Test product 2            2        2               4  0%\n"
        "\n"
        "Yhteensä: 5,00 EUR (Alv 0%, AVL 4§)\n"
        "\n"
        "Tuotteiden nouto & liput:\n"
        "-------------------------\n"
        "\n"
        "Tilaukseenne kuuluvat liput ja tuotteet lunastetaan tapahtuman aikana\n"
        "infotiskiltä. Tuotteiden ja lippujen lunastukseen tarvitaan tosite, joka\n"
        "löytyy allaolevasta osoitteesta. Tositteen voi joko tulostaa tai esittää\n"
        "mm. kännykän tai tabletin näytöltä tapahtuman infotiskillä.\n"
        "\n"
        "https://instanssi.org/store/ta/1234abcd/\n"
        "\n"
        "Huomaathan että lippujen avainkoodit toimivat myös kompojen äänestykseen\n"
        "oikeuttavina avaimina äänestysjärjestelmässämme kompomaatissa. Voit\n"
        "rekisteröidä avaimesi jo ennakkoon kirjautumalla Kompomaattiin osoitteessa\n"
        "https://instanssi.org/kompomaatti/\n"
        "\n"
        "Muista tyhjentää selaimesi sivuhistoria ja välimuisti käytyäsi "
        "lippusivulla, \n"
        "mikäli tietokonettasi käyttää useampi henkilö!\n"
        "\n"
        "-- \n"
        "Instanssi\n"
        "https://instanssi.org\n"
    )


@pytest.mark.django_db
def test_validate_item_ok(store_item):
    validate_item({"item_id": store_item.id, "variant_id": None, "amount": 5})


@pytest.mark.django_db
def test_validate_item_too_much_for_store(store_item):
    store_item.max = 5
    store_item.save()
    with pytest.raises(TransactionException):
        validate_item({"item_id": store_item.id, "variant_id": None, "amount": 6})


@pytest.mark.django_db
def test_validate_item_too_much_per_order(store_item):
    store_item.max = 10
    store_item.max_per_order = 5
    store_item.save()
    with pytest.raises(TransactionException):
        validate_item({"item_id": store_item.id, "variant_id": None, "amount": 6})


@pytest.mark.django_db
def test_validate_item_amount_too_small(store_item):
    store_item.min = 1
    store_item.save()
    with pytest.raises(TransactionException):
        validate_item({"item_id": store_item.id, "variant_id": None, "amount": 0})


@pytest.mark.django_db
def test_validate_item_not_available(store_item):
    store_item.available = False
    store_item.save()
    with pytest.raises(TransactionException):
        validate_item({"item_id": store_item.id, "variant_id": None, "amount": 1})


@pytest.mark.django_db
def test_validate_item_max_is_zero(store_item):
    store_item.max = 0
    store_item.save()
    with pytest.raises(TransactionException):
        validate_item({"item_id": store_item.id, "variant_id": None, "amount": 1})


@pytest.mark.django_db
def test_validate_item_variant_ok(variant_item, store_item_variant, store_item_variant2):
    validate_item({"item_id": variant_item.id, "variant_id": store_item_variant.id, "amount": 1})
    validate_item({"item_id": variant_item.id, "variant_id": store_item_variant2.id, "amount": 1})


@pytest.mark.django_db
def test_validate_item_variant_does_not_belong_to_item(store_item, store_item_variant):
    """Fail if variant does not belong to the product"""
    with pytest.raises(TransactionException):
        validate_item({"item_id": store_item.id, "variant_id": store_item_variant.id, "amount": 1})


@pytest.mark.django_db
def test_validate_payment_method_no_method_ok_for_free_order(store_item):
    store_item.price = Decimal("0")
    store_item.save()
    validate_payment_method(
        items=[{"item_id": store_item.id, "variant_id": None, "amount": 2}],
        method=PaymentMethod.NO_METHOD,
    )


@pytest.mark.django_db
def test_validate_payment_method_no_method_fail_for_expensive_order(store_item):
    store_item.price = Decimal("1.00")  # This is expensive, right ?
    store_item.save()
    with pytest.raises(TransactionException):
        validate_payment_method(
            items=[{"item_id": store_item.id, "variant_id": None, "amount": 2}],
            method=PaymentMethod.NO_METHOD,
        )


@pytest.mark.django_db
def test_validate_payment_method_paytrail_ok(store_item):
    validate_payment_method(
        items=[{"item_id": store_item.id, "variant_id": None, "amount": 2}],
        method=PaymentMethod.PAYTRAIL,
    )


@freeze_time(FAKE_NOW)
@pytest.mark.django_db
def test_create_transaction_ok(transaction_base, store_item, variant_item, store_item_variant):
    transaction = create_store_transaction(
        {
            **transaction_base,
            "items": [
                {"item_id": store_item.id, "variant_id": None, "amount": 1},
                {"item_id": variant_item.id, "variant_id": store_item_variant.id, "amount": 5},
            ],
        }
    )
    assert UUID(transaction.key)
    assert transaction.time_created == FAKE_NOW
    assert transaction.firstname == "Donald"
    assert transaction.lastname == "Duck"
    assert transaction.company == "Duck Co"
    assert transaction.email == "donald.duck@duckburg.inv"
    assert transaction.telephone == "991234567"
    assert transaction.mobile == "+358991234567"
    assert transaction.street == "1313 Webfoot Walk"
    assert transaction.postalcode == "00000"
    assert transaction.city == "Duckburg"
    assert transaction.country == "US"
    assert transaction.information == "Quack, damn you!"
    assert transaction.token == ""
    assert transaction.time_pending is None
    assert transaction.time_cancelled is None
    assert transaction.time_paid is None
    assert transaction.payment_method_name == ""

    # Test properties
    assert transaction.is_cancelled is False
    assert transaction.is_delivered is False
    assert transaction.is_pending is False
    assert transaction.is_paid is False
    assert transaction.full_name == "Donald Duck"

    # Make sure this doesn't crash
    assert transaction.qr_code.startswith("http")

    # Check price functions
    assert transaction.get_transaction_items().count() == 6
    assert transaction.get_total_price() == Decimal("120.0")
    assert transaction.get_storeitem_count(store_item) == 1
    assert transaction.get_storeitem_count(variant_item) == 5

    # Make sure transaction items went through
    for transaction_item in transaction.get_transaction_items():
        assert transaction_item.item.id in [store_item.id, variant_item.id]
        if transaction_item.item_id == variant_item.id:
            assert transaction_item.variant_id == store_item_variant.id
        else:
            assert transaction_item.variant is None
        assert transaction_item.time_delivered is None
        assert UUID(transaction_item.key)
        assert transaction_item.is_delivered is False
        assert transaction_item.qr_code.startswith("http") is True

    # Check amounts (manually)
    assert TransactionItem.objects.filter(transaction=transaction, item=store_item).count() == 1
    assert TransactionItem.objects.filter(transaction=transaction, item=variant_item).count() == 5

    # Make sure prices were set
    bought_items = TransactionItem.objects.filter(
        transaction=transaction, item__in=[store_item.id, variant_item.id]
    )
    for item in bought_items:
        assert item.original_price == Decimal("20")
        assert item.purchase_price == Decimal("20")


@pytest.mark.django_db
def test_create_transaction_with_discounts_trigger_discount(transaction_base, discount_item):
    transaction = create_store_transaction(
        {
            **transaction_base,
            "items": [
                {"item_id": discount_item.id, "variant_id": None, "amount": 5},  # 5 should trigger discount
            ],
        }
    )

    # Internal API should return proper results
    assert transaction.get_total_price() == Decimal("50.0")  # (5 * 20e) * 0.5

    # Make sure database seems fine, too
    discount_items = TransactionItem.objects.filter(transaction=transaction, item=discount_item)
    for item in discount_items:
        assert item.original_price == Decimal("20")
        assert item.purchase_price == Decimal("10")


@pytest.mark.django_db
def test_create_transaction_with_discounts_but_dont_trigger_discount(transaction_base, discount_item):
    transaction = create_store_transaction(
        {
            **transaction_base,
            "items": [
                {
                    "item_id": discount_item.id,
                    "variant_id": None,
                    "amount": 4,
                },  # 5 should NOT trigger discount
            ],
        }
    )

    # Internal API should return proper results
    assert transaction.get_total_price() == Decimal("80.0")  # 4 * 20e

    # Make sure database seems fine, too
    discount_items = TransactionItem.objects.filter(transaction=transaction, item=discount_item)
    for item in discount_items:
        assert item.original_price == Decimal("20")
        assert item.purchase_price == Decimal("20")
