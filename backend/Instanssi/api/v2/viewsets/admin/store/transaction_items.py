from django.db.models import QuerySet
from rest_framework import serializers
from rest_framework.serializers import BaseSerializer

from Instanssi.api.v2.serializers.admin.store import TransactionItemSerializer
from Instanssi.api.v2.utils.base import PermissionViewSet
from Instanssi.store.models import StoreItem, TransactionItem


class TransactionItemViewSet(PermissionViewSet):
    """Staff viewset for managing transaction items."""

    queryset = TransactionItem.objects.all()
    serializer_class = TransactionItemSerializer  # type: ignore[assignment]
    ordering_fields = ("id", "item", "transaction", "purchase_price", "time_delivered")
    search_fields = ("key", "transaction__firstname", "transaction__lastname", "transaction__email")
    filterset_fields = ("item", "transaction", "variant")

    def get_queryset(self) -> QuerySet[TransactionItem]:
        """Filter transaction items by event."""
        event_id = int(self.kwargs["event_pk"])
        return self.queryset.filter(item__event_id=event_id).order_by("-id")

    def validate_item_belongs_to_event(self, item: StoreItem) -> None:
        """Validate that the item belongs to the event from the URL."""
        event_id = int(self.kwargs["event_pk"])
        if item.event_id != event_id:
            raise serializers.ValidationError({"item": ["Item does not belong to this event"]})

    def perform_update(self, serializer: BaseSerializer[TransactionItem]) -> None:  # type: ignore[override]
        if item := serializer.validated_data.get("item"):
            self.validate_item_belongs_to_event(item)
        super().perform_update(serializer)  # type: ignore[arg-type]
