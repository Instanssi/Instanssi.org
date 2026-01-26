from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import LimitOffsetPagination

from Instanssi.api.v2.serializers.store import StoreItemVariantSerializer
from Instanssi.api.v2.utils.base import PermissionViewSet
from Instanssi.store.models import StoreItemVariant


class StoreItemVariantViewSet(PermissionViewSet):
    """ViewSet for StoreItemVariant model (staff access only).

    Staff access (requires store.view/add/change/delete_storeitemvariant permissions):
    - GET: List/retrieve all store item variants for the event
    - POST: Create new store item variants
    - PUT/PATCH: Update store item variants
    - DELETE: Delete store item variants

    Variants can also be viewed nested in the StoreItem response.
    """

    queryset = StoreItemVariant.objects.all()
    serializer_class = StoreItemVariantSerializer  # type: ignore[assignment]
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    ordering_fields = ("id", "item", "name")
    search_fields = ("name",)
    filterset_fields = ("item",)

    def get_queryset(self) -> QuerySet[StoreItemVariant]:
        """Filter variants by event (through item)."""
        event_id = int(self.kwargs["event_pk"])
        return self.queryset.filter(item__event_id=event_id).order_by("id")
