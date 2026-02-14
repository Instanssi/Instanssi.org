import logging
from typing import Any

from django.http import HttpRequest
from rest_framework.serializers import (
    BooleanField,
    CharField,
    ChoiceField,
    EmailField,
    IntegerField,
    ModelSerializer,
    Serializer,
    SerializerMethodField,
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
from Instanssi.store.models import StoreItem, StoreItemVariant, StoreTransaction

logger = logging.getLogger(__name__)


class StoreItemVariantSerializer(ModelSerializer[StoreItemVariant]):
    class Meta:
        model = StoreItemVariant
        fields = ("id", "name")


class StoreItemSerializer(ModelSerializer[StoreItem]):
    imagefile_original_url = SerializerMethodField()
    imagefile_thumbnail_url = SerializerMethodField()
    discount_factor = SerializerMethodField()
    variants = StoreItemVariantSerializer(many=True)

    def get_imagefile_original_url(self, obj: StoreItem) -> str | None:
        if not obj.imagefile_original:
            return None
        request: HttpRequest = self.context["request"]
        return request.build_absolute_uri(obj.imagefile_original.url)

    def get_imagefile_thumbnail_url(self, obj: StoreItem) -> str | None:
        if not obj.imagefile_thumbnail:
            return None
        request: HttpRequest = self.context["request"]
        return request.build_absolute_uri(obj.imagefile_thumbnail.url)

    def get_discount_factor(self, obj: StoreItem) -> float:
        return obj.get_discount_factor()

    class Meta:
        model = StoreItem
        fields = (
            "id",
            "event",
            "name",
            "description",
            "price",
            "max",
            "available",
            "imagefile_original_url",
            "imagefile_thumbnail_url",
            "max_per_order",
            "sort_index",
            "discount_amount",
            "discount_percentage",
            "is_discount_available",
            "discount_factor",
            "num_available",
            "variants",
        )
        extra_kwargs: dict[str, dict[str, object]] = {}


class StoreTransactionItemSerializer(Serializer[dict[str, Any]]):
    item_id = IntegerField()
    variant_id = IntegerField(allow_null=True)
    amount = IntegerField(min_value=1)

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        data = super(StoreTransactionItemSerializer, self).validate(data)
        try:
            validate_item(data)
        except TransactionException as e:
            raise ValidationError(str(e))
        return data


class StoreTransactionSerializer(Serializer[StoreTransaction]):
    first_name = CharField(max_length=64)
    last_name = CharField(max_length=64)
    company = CharField(allow_blank=True, max_length=128)
    email = EmailField(max_length=255)
    telephone = CharField(allow_blank=True, max_length=64)
    mobile = CharField(allow_blank=True, max_length=64)
    street = CharField(max_length=128)
    postal_code = CharField(max_length=16)
    city = CharField(max_length=64)
    country = CharField(max_length=2)
    information = CharField(allow_blank=True, max_length=1024)
    payment_method = ChoiceField(choices=[e.value for e in PaymentMethod])
    read_terms = BooleanField()
    discount_key = CharField(allow_blank=True, required=False, max_length=32)
    items = StoreTransactionItemSerializer(many=True, required=True)
    save = BooleanField(default=False)  # type: ignore[assignment]

    def validate_read_terms(self, value: bool | None) -> bool | None:
        if not value:
            raise ValidationError("Käyttöehdot tulee hyväksyä ennen kuin tilausta voidaan jatkaa")
        return value

    def validate_items(self, value: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
        if not value:
            raise ValidationError("Ostoskorissa on oltava vähintään yksi tuote")
        serializer = StoreTransactionItemSerializer(data=value, many=True)
        serializer.is_valid(raise_exception=True)
        try:
            validate_items(value)
        except TransactionException as e:
            raise ValidationError(str(e))
        return value

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        data = super(StoreTransactionSerializer, self).validate(data)
        try:
            validate_payment_method(data["items"], PaymentMethod(data["payment_method"]))
        except TransactionException as e:
            raise ValidationError(str(e))
        return data

    def create(self, validated_data: dict[str, Any]) -> StoreTransaction:
        return create_store_transaction(validated_data)
