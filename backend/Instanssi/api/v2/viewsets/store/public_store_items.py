from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet

from Instanssi.api.v2.serializers.store import PublicStoreItemSerializer
from Instanssi.store.models import StoreItem


class PublicStoreItemViewSet(ReadOnlyModelViewSet[StoreItem]):
    """Public read-only ViewSet for StoreItem model.

    This endpoint is accessible without authentication and returns only
    available store items. Supports secret_key query parameter to reveal
    hidden items.

    Does NOT expose sensitive fields like is_secret, secret_key, or is_ticket.

    Similar to v1 /api/v1/store_items/ endpoint.
    """

    serializer_class = PublicStoreItemSerializer
    permission_classes = [AllowAny]
    authentication_classes: list[type] = []
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    ordering_fields = ("id", "event", "name", "price", "sort_index")
    filterset_fields = ("event",)

    def get_queryset(self) -> QuerySet[StoreItem]:
        """Return only visible store items, respecting secret_key."""
        secret_key = self.request.query_params.get("secret_key")
        return StoreItem.items_visible(secret_key=secret_key).order_by("sort_index")
