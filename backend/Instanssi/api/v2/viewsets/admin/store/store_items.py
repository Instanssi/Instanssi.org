from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.serializers import BaseSerializer

from Instanssi.api.v2.serializers.admin.store import StoreItemSerializer
from Instanssi.api.v2.utils.base import PermissionViewSet
from Instanssi.store.models import StoreItem


class StoreItemViewSet(PermissionViewSet):
    """ViewSet for StoreItem model (staff access only).

    This endpoint is for event-scoped staff management of store items.
    For public read access, use /api/v2/store/items/ instead.

    Staff access (requires store.view/add/change/delete_storeitem permissions):
    - GET: List/retrieve all store items for the event
    - POST: Create new store items
    - PUT/PATCH: Update store items
    - DELETE: Delete store items
    """

    queryset = StoreItem.objects.all()
    serializer_class = StoreItemSerializer  # type: ignore[assignment]
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    ordering_fields = ("id", "event", "name", "price", "sort_index")
    filterset_fields = ("event", "available", "is_ticket", "is_secret")

    def get_queryset(self) -> QuerySet[StoreItem]:
        """Filter store items by event."""
        event_id = int(self.kwargs["event_pk"])
        return self.queryset.filter(event_id=event_id).order_by("sort_index")

    def perform_create(self, serializer: BaseSerializer[StoreItem]) -> None:  # type: ignore[override]
        """Set event from URL when creating."""
        serializer.save(event_id=int(self.kwargs["event_pk"]))
