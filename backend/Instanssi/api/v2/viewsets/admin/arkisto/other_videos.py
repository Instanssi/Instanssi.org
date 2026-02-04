from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.serializers import BaseSerializer

from Instanssi.api.v2.serializers.admin.arkisto import OtherVideoSerializer
from Instanssi.api.v2.utils.base import PermissionViewSet
from Instanssi.arkisto.models import OtherVideo, OtherVideoCategory


class OtherVideoViewSet(PermissionViewSet):
    """Staff viewset for managing archive videos."""

    queryset = OtherVideo.objects.all()
    serializer_class = OtherVideoSerializer  # type: ignore[assignment]
    ordering_fields = ("id", "name", "category")
    search_fields = ("name", "description")
    filterset_fields = ("category",)

    def get_queryset(self) -> QuerySet[OtherVideo]:
        """Filter videos by event from URL (via category)."""
        event_id = int(self.kwargs["event_pk"])
        return (
            self.queryset.filter(category__event_id=event_id)
            .select_related("category")
            .order_by("category__name", "name")
        )

    def validate_category_belongs_to_event(self, category: OtherVideoCategory) -> None:
        """Validate that the category belongs to the event from the URL."""
        event_id = int(self.kwargs["event_pk"])
        if category.event_id != event_id:
            raise serializers.ValidationError({"category": [_("Category does not belong to this event")]})

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
