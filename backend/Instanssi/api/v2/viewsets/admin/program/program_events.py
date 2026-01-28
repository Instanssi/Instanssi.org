from django.db.models import QuerySet
from rest_framework.serializers import BaseSerializer

from Instanssi.api.v2.serializers.admin.program import ProgramEventSerializer
from Instanssi.api.v2.utils.base import PermissionViewSet
from Instanssi.ext_programme.models import ProgrammeEvent


class ProgramEventViewSet(PermissionViewSet):
    """Staff viewset for managing program events."""

    queryset = ProgrammeEvent.objects.all()
    serializer_class = ProgramEventSerializer  # type: ignore[assignment]
    ordering_fields = ("id", "start", "end", "title", "event_type")
    search_fields = ("title", "description", "presenters", "place")
    filterset_fields = ("active", "event_type")

    def get_queryset(self) -> QuerySet[ProgrammeEvent]:
        """Filter program events by event from URL."""
        event_id = int(self.kwargs["event_pk"])
        return self.queryset.filter(event_id=event_id).order_by("start")

    def perform_create(self, serializer: BaseSerializer[ProgrammeEvent]) -> None:  # type: ignore[override]
        """Set event from URL when creating."""
        serializer.save(event_id=int(self.kwargs["event_pk"]))
