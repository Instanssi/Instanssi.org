from rest_framework.serializers import ModelSerializer, SerializerMethodField

from Instanssi.store.models import TransactionItem


class TransactionItemSerializer(ModelSerializer[TransactionItem]):
    """Serializer for TransactionItem model (staff access)."""

    is_delivered = SerializerMethodField()

    def get_is_delivered(self, obj: TransactionItem) -> bool:
        return obj.is_delivered

    class Meta:
        model = TransactionItem
        fields = (
            "id",
            "key",
            "item",
            "variant",
            "transaction",
            "time_delivered",
            "purchase_price",
            "original_price",
            "is_delivered",
        )
        read_only_fields = (
            "id",
            "key",
            "is_delivered",
        )
