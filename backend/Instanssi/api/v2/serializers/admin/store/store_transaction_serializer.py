from rest_framework.serializers import ModelSerializer, SerializerMethodField

from Instanssi.api.v2.serializers.admin.store.nested_receipt_serializer import (
    NestedReceiptSerializer,
)
from Instanssi.api.v2.serializers.admin.store.store_transaction_event_serializer import (
    StoreTransactionEventSerializer,
)
from Instanssi.store.models import StoreTransaction


class StoreTransactionSerializer(ModelSerializer[StoreTransaction]):
    """Serializer for StoreTransaction model (staff access)."""

    is_paid = SerializerMethodField()
    is_cancelled = SerializerMethodField()
    is_pending = SerializerMethodField()
    is_delivered = SerializerMethodField()
    full_name = SerializerMethodField()
    status_text = SerializerMethodField()
    total_price = SerializerMethodField()
    events = StoreTransactionEventSerializer(many=True, read_only=True, source="storetransactionevent_set")
    receipts = NestedReceiptSerializer(many=True, read_only=True, source="receipt_set")

    def get_is_paid(self, obj: StoreTransaction) -> bool:
        return obj.is_paid

    def get_is_cancelled(self, obj: StoreTransaction) -> bool:
        return obj.is_cancelled

    def get_is_pending(self, obj: StoreTransaction) -> bool:
        return obj.is_pending

    def get_is_delivered(self, obj: StoreTransaction) -> bool:
        return obj.is_delivered

    def get_full_name(self, obj: StoreTransaction) -> str:
        return obj.full_name

    def get_status_text(self, obj: StoreTransaction) -> str:
        return obj.get_status_text()

    def get_total_price(self, obj: StoreTransaction) -> str:
        return str(obj.get_total_price())

    class Meta:
        model = StoreTransaction
        fields = (
            "id",
            "token",
            "time_created",
            "time_paid",
            "time_pending",
            "time_cancelled",
            "payment_method_name",
            "key",
            "firstname",
            "lastname",
            "company",
            "email",
            "telephone",
            "mobile",
            "street",
            "postalcode",
            "city",
            "country",
            "information",
            "is_paid",
            "is_cancelled",
            "is_pending",
            "is_delivered",
            "full_name",
            "status_text",
            "total_price",
            "events",
            "receipts",
        )
        read_only_fields = (
            "id",
            "token",
            "key",
            "is_paid",
            "is_cancelled",
            "is_pending",
            "is_delivered",
            "full_name",
            "status_text",
            "total_price",
            "events",
            "receipts",
        )
