from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import SAFE_METHODS
from rest_framework.request import Request
from rest_framework.serializers import BaseSerializer
from rest_framework.views import APIView

from Instanssi.api.v2.serializers.arkisto import OtherVideoSerializer
from Instanssi.api.v2.utils.base import PermissionViewSet, PublicReadPermission
from Instanssi.arkisto.models import OtherVideo, OtherVideoCategory


class ArchivedEventVideoReadPermission(PublicReadPermission):
    """Allow read access for videos in archived events, full permissions for staff."""

    def has_object_permission(self, request: Request, view: APIView, obj: OtherVideo) -> bool:
        if request.method in SAFE_METHODS and obj.category.event.archived:
            return True
        return super().has_permission(request, view)


class OtherVideoViewSet(PermissionViewSet):
    """
    Videos for archived events.

    Public users can read videos for archived events.
    Staff with arkisto permissions can manage all videos.
    """

    queryset = OtherVideo.objects.all()
    serializer_class = OtherVideoSerializer  # type: ignore[assignment]
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    ordering_fields = ("id", "name", "category")
    search_fields = ("name", "description")
    filterset_fields = ("category",)
    permission_classes = [ArchivedEventVideoReadPermission]

    def get_queryset(self) -> QuerySet[OtherVideo]:
        """Filter videos by event from URL (via category)."""
        event_id = int(self.kwargs["event_pk"])
        queryset = self.queryset.filter(category__event_id=event_id).select_related("category")

        # For non-staff users, only show videos for archived events
        if not self.request.user.is_authenticated or not self.request.user.has_perm(
            "arkisto.view_othervideo"
        ):
            queryset = queryset.filter(category__event__archived=True)

        return queryset.order_by("category__name", "name")

    def validate_category_belongs_to_event(self, category: OtherVideoCategory) -> None:
        """Validate that the category belongs to the event from the URL."""
        event_id = int(self.kwargs["event_pk"])
        if category.event_id != event_id:
            raise serializers.ValidationError({"category": ["Category does not belong to this event"]})

    def perform_create(self, serializer: BaseSerializer[OtherVideo]) -> None:  # type: ignore[override]
        """Validate category belongs to event before creating."""
        if category := serializer.validated_data.get("category"):
            self.validate_category_belongs_to_event(category)
        super().perform_create(serializer)  # type: ignore[arg-type]

    def perform_update(self, serializer: BaseSerializer[OtherVideo]) -> None:  # type: ignore[override]
        """Validate category belongs to event if being changed."""
        if category := serializer.validated_data.get("category"):
            self.validate_category_belongs_to_event(category)
        super().perform_update(serializer)  # type: ignore[arg-type]
