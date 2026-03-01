from django.db.models import QuerySet
from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.serializers import BaseSerializer

from Instanssi.api.v2.serializers.admin.store import StoreItemSerializer
from Instanssi.api.v2.utils.base import PermissionViewSet
from Instanssi.store.models import StoreItem


class StoreItemViewSet(PermissionViewSet):
    """Staff viewset for managing store items."""

    parser_classes = (MultiPartParser, FormParser)
    queryset = StoreItem.objects.all()
    serializer_class = StoreItemSerializer  # type: ignore[assignment]
    ordering_fields = ("id", "event", "name", "price", "max", "sort_index")
    search_fields = ("name", "description")
    filterset_fields = ("event", "available", "is_ticket", "is_secret")

    def get_queryset(self) -> QuerySet[StoreItem]:
        """Filter store items by event."""
        event_id = int(self.kwargs["event_pk"])
        return self.queryset.filter(event_id=event_id).order_by("sort_index")

    def perform_create(self, serializer: BaseSerializer[StoreItem]) -> None:  # type: ignore[override]
        """Set event from URL when creating."""
        serializer.save(event_id=int(self.kwargs["event_pk"]))

    def perform_destroy(self, instance: StoreItem) -> None:  # type: ignore[override]
        """Prevent deletion of store items that have been sold."""
        if instance.num_sold() > 0:
            raise serializers.ValidationError(
                {"detail": _("Cannot delete a store item that has sold units.")}
            )
        super().perform_destroy(instance)
