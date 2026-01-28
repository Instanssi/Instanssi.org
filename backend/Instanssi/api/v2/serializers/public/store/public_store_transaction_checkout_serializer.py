from typing import Any

from rest_framework.serializers import (
    BooleanField,
    CharField,
    ChoiceField,
    EmailField,
    IntegerField,
    Serializer,
)

from Instanssi.store.methods import PaymentMethod
from Instanssi.store.models import StoreTransaction


class PublicStoreTransactionCheckoutItemSerializer(Serializer[dict[str, Any]]):
    """Serializer for individual items in a public checkout request."""

    item_id = IntegerField()
    variant_id = IntegerField(allow_null=True)
    amount = IntegerField(min_value=1)


class PublicStoreTransactionCheckoutSerializer(Serializer[StoreTransaction]):
    """Public serializer for creating a new store transaction (checkout).

    This is a write-only serializer for anonymous checkout.
    No authentication is required.
    """

    first_name = CharField(max_length=64)
    last_name = CharField(max_length=64)
    company = CharField(allow_blank=True, max_length=128, required=False, default="")
    email = EmailField(max_length=255)
    telephone = CharField(allow_blank=True, max_length=64, required=False, default="")
    mobile = CharField(allow_blank=True, max_length=64, required=False, default="")
    street = CharField(max_length=128)
    postal_code = CharField(max_length=16)
    city = CharField(max_length=64)
    country = CharField(max_length=2)
    information = CharField(allow_blank=True, max_length=1024, required=False, default="")
    payment_method = ChoiceField(choices=[e.value for e in PaymentMethod])
    read_terms = BooleanField()
    items = PublicStoreTransactionCheckoutItemSerializer(many=True, required=True)
    confirm = BooleanField(default=False)
