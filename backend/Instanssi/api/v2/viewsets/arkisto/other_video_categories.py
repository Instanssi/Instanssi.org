from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import SAFE_METHODS
from rest_framework.request import Request
from rest_framework.serializers import BaseSerializer
from rest_framework.views import APIView

from Instanssi.api.v2.serializers.arkisto import OtherVideoCategorySerializer
from Instanssi.api.v2.utils.base import FullDjangoModelPermissions, PermissionViewSet
from Instanssi.arkisto.models import OtherVideoCategory


class ArchivedEventReadPermission(FullDjangoModelPermissions):
    """Allow read access for archived events, full permissions for staff."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return super().has_permission(request, view)

    def has_object_permission(self, request: Request, view: APIView, obj: OtherVideoCategory) -> bool:
        if request.method in SAFE_METHODS and obj.event.archived:
            return True
        return super().has_permission(request, view)


class OtherVideoCategoryViewSet(PermissionViewSet):
    """
    Video categories for archived events.

    Public users can read video categories for archived events.
    Staff with arkisto permissions can manage all video categories.
    """

    queryset = OtherVideoCategory.objects.all()
    serializer_class = OtherVideoCategorySerializer  # type: ignore[assignment]
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    ordering_fields = ("id", "name")
    search_fields = ("name",)
    permission_classes = [ArchivedEventReadPermission]

    def get_queryset(self) -> QuerySet[OtherVideoCategory]:
        """Filter video categories by event from URL."""
        event_id = int(self.kwargs["event_pk"])
        queryset = self.queryset.filter(event_id=event_id)

        # For non-staff users, only show categories for archived events
        if not self.request.user.is_authenticated or not self.request.user.has_perm(
            "arkisto.view_othervideocategory"
        ):
            queryset = queryset.filter(event__archived=True)

        return queryset.order_by("name")

    def perform_create(self, serializer: BaseSerializer[OtherVideoCategory]) -> None:  # type: ignore[override]
        """Set event from URL when creating."""
        serializer.save(event_id=int(self.kwargs["event_pk"]))
