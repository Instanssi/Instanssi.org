from django.db.models import QuerySet
from rest_framework import serializers
from rest_framework.serializers import BaseSerializer

from Instanssi.api.v2.serializers.admin.kompomaatti import CompetitionSerializer
from Instanssi.api.v2.utils.base import PermissionViewSet
from Instanssi.kompomaatti.models import Competition, CompetitionParticipation


class CompetitionViewSet(PermissionViewSet):
    """Staff viewset for managing competitions."""

    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer  # type: ignore[assignment]
    ordering_fields = ("id", "event", "name", "participation_end", "start", "end", "active")
    search_fields = ("name", "description")
    filterset_fields = ("active", "show_results", "hide_from_archive")

    def get_queryset(self) -> QuerySet[Competition]:
        """Filter competitions by event from URL."""
        event_id = int(self.kwargs["event_pk"])
        return self.queryset.filter(event_id=event_id)

    def perform_create(self, serializer: BaseSerializer[Competition]) -> None:  # type: ignore[override]
        """Set event from URL when creating."""
        serializer.save(event_id=int(self.kwargs["event_pk"]))

    def perform_destroy(self, instance: Competition) -> None:  # type: ignore[override]
        """Prevent deletion of competitions that have participations."""
        if CompetitionParticipation.objects.filter(competition=instance).exists():
            raise serializers.ValidationError(
                {"detail": "Cannot delete a competition that has participations."}
            )
        super().perform_destroy(instance)
