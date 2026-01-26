from rest_framework.serializers import ModelSerializer, SerializerMethodField

from Instanssi.store.models import Receipt


class NestedReceiptSerializer(ModelSerializer[Receipt]):
    """Serializer for Receipt model (nested in transaction response)."""

    is_sent = SerializerMethodField()

    def get_is_sent(self, obj: Receipt) -> bool:
        return obj.is_sent

    class Meta:
        model = Receipt
        fields = ("id", "subject", "mail_to", "mail_from", "sent", "is_sent")
        read_only_fields = ("id", "subject", "mail_to", "mail_from", "sent", "is_sent")
