from django.db.models import QuerySet
from rest_framework.serializers import BaseSerializer

from Instanssi.api.v2.serializers.admin.kompomaatti import CompoSerializer
from Instanssi.api.v2.utils.base import PermissionViewSet
from Instanssi.kompomaatti.models import Compo


class CompoViewSet(PermissionViewSet):
    """Staff viewset for managing compos."""

    queryset = Compo.objects.all()
    serializer_class = CompoSerializer  # type: ignore[assignment]
    ordering_fields = ("id", "event", "name", "compo_start", "voting_start")
    search_fields = ("name", "description")
    filterset_fields = (
        "active",
        "show_voting_results",
        "is_votable",
        "hide_from_archive",
        "hide_from_frontpage",
    )

    def get_queryset(self) -> QuerySet[Compo]:
        """Filter compos by event from URL."""
        event_id = int(self.kwargs["event_pk"])
        return self.queryset.filter(event_id=event_id)

    def perform_create(self, serializer: BaseSerializer[Compo]) -> None:  # type: ignore[override]
        """Set event from URL when creating."""
        serializer.save(event_id=int(self.kwargs["event_pk"]))
