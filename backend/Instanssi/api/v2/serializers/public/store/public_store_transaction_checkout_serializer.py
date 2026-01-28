from typing import Any

from rest_framework.serializers import (
    BooleanField,
    CharField,
    ChoiceField,
    EmailField,
    IntegerField,
    Serializer,
    ValidationError,
)

from Instanssi.store.handlers import (
    TransactionException,
    create_store_transaction,
    validate_item,
    validate_items,
    validate_payment_method,
)
from Instanssi.store.methods import PaymentMethod
from Instanssi.store.models import StoreTransaction


class PublicStoreTransactionCheckoutItemSerializer(Serializer[dict[str, Any]]):
    """Serializer for individual items in a public checkout request."""

    item_id = IntegerField()
    variant_id = IntegerField(allow_null=True)
    amount = IntegerField(min_value=1)

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        data = super().validate(data)
        try:
            validate_item(data)
        except TransactionException as e:
            raise ValidationError(str(e))
        return data


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

    def validate_read_terms(self, value: bool | None) -> bool | None:
        if not value:
            raise ValidationError("Terms and conditions must be accepted before proceeding with the order")
        return value

    def validate_items(self, value: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
        if not value:
            raise ValidationError("Shopping cart must contain at least one item")
        try:
            validate_items(value)
        except TransactionException as e:
            raise ValidationError(str(e))
        return value

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        data = super().validate(data)
        try:
            validate_payment_method(data["items"], PaymentMethod(data["payment_method"]))
        except TransactionException as e:
            raise ValidationError(str(e))
        return data

    def create(self, validated_data: dict[str, Any]) -> StoreTransaction:
        return create_store_transaction(validated_data)
