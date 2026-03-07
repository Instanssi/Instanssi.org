from rest_framework.serializers import ModelSerializer, SerializerMethodField

from Instanssi.store.models import StoreTransaction


class InfodeskTransactionSerializer(ModelSerializer[StoreTransaction]):
    """Read-only serializer for infodesk transaction lookup."""

    is_paid = SerializerMethodField()
    is_cancelled = SerializerMethodField()
    is_pending = SerializerMethodField()
    is_delivered = SerializerMethodField()
    full_name = SerializerMethodField()
    status_text = SerializerMethodField()

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

    class Meta:
        model = StoreTransaction
        fields = (
            "id",
            "time_created",
            "time_paid",
            "time_cancelled",
            "firstname",
            "lastname",
            "email",
            "company",
            "telephone",
            "mobile",
            "information",
            "is_paid",
            "is_cancelled",
            "is_pending",
            "is_delivered",
            "full_name",
            "status_text",
        )
        read_only_fields = fields
