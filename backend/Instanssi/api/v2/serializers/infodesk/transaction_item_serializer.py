from rest_framework.serializers import ModelSerializer, SerializerMethodField

from Instanssi.store.models import TransactionItem


class InfodeskTransactionItemSerializer(ModelSerializer[TransactionItem]):
    """Read-only serializer for infodesk transaction item lookup."""

    is_delivered = SerializerMethodField()
    item_name = SerializerMethodField()
    variant_name = SerializerMethodField()
    transaction_full_name = SerializerMethodField()
    transaction_is_paid = SerializerMethodField()

    def get_is_delivered(self, obj: TransactionItem) -> bool:
        return obj.is_delivered

    def get_item_name(self, obj: TransactionItem) -> str:
        return obj.item.name

    def get_variant_name(self, obj: TransactionItem) -> str | None:
        if obj.variant:
            return obj.variant.name
        return None

    def get_transaction_full_name(self, obj: TransactionItem) -> str:
        return obj.transaction.full_name

    def get_transaction_is_paid(self, obj: TransactionItem) -> bool:
        return obj.transaction.is_paid

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
            "is_delivered",
            "item_name",
            "variant_name",
            "transaction_full_name",
            "transaction_is_paid",
        )
        read_only_fields = fields
