from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.serializers import BaseSerializer

from Instanssi.api.v2.serializers.store import TransactionItemSerializer
from Instanssi.api.v2.utils.base import PermissionViewSet
from Instanssi.store.models import StoreItem, TransactionItem


class TransactionItemViewSet(PermissionViewSet):
    """ViewSet for TransactionItem model (staff access).

    Staff access (requires store.view/add/change/delete_transactionitem permissions):
    - GET: List/retrieve all transaction items
    - POST: Create new transaction items
    - PUT/PATCH: Update transaction items (e.g., mark as delivered)
    - DELETE: Delete transaction items
    """

    queryset = TransactionItem.objects.all()
    serializer_class = TransactionItemSerializer  # type: ignore[assignment]
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    ordering_fields = ("id", "item", "transaction", "time_delivered")
    search_fields = ("key", "transaction__firstname", "transaction__lastname", "transaction__email")
    filterset_fields = ("item", "transaction", "variant")

    def get_queryset(self) -> QuerySet[TransactionItem]:
        """Filter transaction items by event if specified."""
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
