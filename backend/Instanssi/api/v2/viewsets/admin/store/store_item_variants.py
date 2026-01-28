from django.db.models import QuerySet

from Instanssi.api.v2.serializers.admin.store import StoreItemVariantSerializer
from Instanssi.api.v2.utils.base import PermissionViewSet
from Instanssi.store.models import StoreItemVariant


class StoreItemVariantViewSet(PermissionViewSet):
    """Staff viewset for managing store item variants."""

    queryset = StoreItemVariant.objects.all()
    serializer_class = StoreItemVariantSerializer  # type: ignore[assignment]
    ordering_fields = ("id", "item", "name")
    search_fields = ("name",)
    filterset_fields = ("item",)

    def get_queryset(self) -> QuerySet[StoreItemVariant]:
        """Filter variants by event (through item)."""
        event_id = int(self.kwargs["event_pk"])
        return self.queryset.filter(item__event_id=event_id).order_by("id")
