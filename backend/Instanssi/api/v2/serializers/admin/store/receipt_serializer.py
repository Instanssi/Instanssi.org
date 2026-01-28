from rest_framework.serializers import ModelSerializer, SerializerMethodField

from Instanssi.store.models import Receipt


class ReceiptSerializer(ModelSerializer[Receipt]):
    """Serializer for Receipt model (staff access)."""

    is_sent = SerializerMethodField()

    def get_is_sent(self, obj: Receipt) -> bool:
        return obj.is_sent

    class Meta:
        model = Receipt
        fields = (
            "id",
            "transaction",
            "subject",
            "mail_to",
            "mail_from",
            "sent",
            "params",
            "content",
            "is_sent",
        )
        read_only_fields = (
            "id",
            "sent",
            "is_sent",
        )
