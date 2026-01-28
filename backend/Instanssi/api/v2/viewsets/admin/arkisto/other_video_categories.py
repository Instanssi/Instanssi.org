from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.serializers import BaseSerializer

from Instanssi.api.v2.serializers.admin.arkisto import OtherVideoCategorySerializer
from Instanssi.api.v2.utils.base import PermissionViewSet
from Instanssi.arkisto.models import OtherVideoCategory


class OtherVideoCategoryViewSet(PermissionViewSet):
    """Staff viewset for managing archive video categories."""

    queryset = OtherVideoCategory.objects.all()
    serializer_class = OtherVideoCategorySerializer  # type: ignore[assignment]
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    ordering_fields = ("id", "name")
    search_fields = ("name",)

    def get_queryset(self) -> QuerySet[OtherVideoCategory]:
        """Filter video categories by event from URL."""
        event_id = int(self.kwargs["event_pk"])
        return self.queryset.filter(event_id=event_id).order_by("name")

    def perform_create(self, serializer: BaseSerializer[OtherVideoCategory]) -> None:  # type: ignore[override]
        """Set event from URL when creating."""
        serializer.save(event_id=int(self.kwargs["event_pk"]))
