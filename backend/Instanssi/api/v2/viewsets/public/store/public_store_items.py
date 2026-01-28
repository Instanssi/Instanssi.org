from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from Instanssi.api.v2.serializers.public.store import PublicStoreItemSerializer
from Instanssi.api.v2.utils.base import PublicReadOnlyViewSet
from Instanssi.store.models import StoreItem


class PublicStoreItemViewSet(PublicReadOnlyViewSet[StoreItem]):
    """Public read-only endpoint for store items.

    Returns only available store items. Supports secret_key query parameter
    to reveal hidden items.
    """

    serializer_class = PublicStoreItemSerializer
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    ordering_fields = ("id", "event", "name", "price", "sort_index")
    filterset_fields = ("event",)

    def get_queryset(self) -> QuerySet[StoreItem]:
        secret_key = self.request.query_params.get("secret_key")
        return StoreItem.items_visible(secret_key=secret_key).order_by("sort_index")
