from rest_framework.serializers import ModelSerializer

from Instanssi.store.models import StoreTransactionEvent


class StoreTransactionEventSerializer(ModelSerializer[StoreTransactionEvent]):
    """Serializer for StoreTransactionEvent model (nested in transaction)."""

    class Meta:
        model = StoreTransactionEvent
        fields = ("id", "message", "data", "created")
        read_only_fields = ("id", "message", "data", "created")
