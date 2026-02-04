from django.db.models import QuerySet
from rest_framework import serializers
from rest_framework.serializers import BaseSerializer

from Instanssi.api.v2.serializers.admin.kompomaatti import (
    CompetitionParticipationSerializer,
)
from Instanssi.api.v2.utils.base import PermissionViewSet
from Instanssi.kompomaatti.models import Competition, CompetitionParticipation


class CompetitionParticipationViewSet(PermissionViewSet):
    """Staff viewset for managing competition participations.

    Supports ordering by rank and score.
    """

    queryset = CompetitionParticipation.objects.all()
    serializer_class = CompetitionParticipationSerializer  # type: ignore[assignment]
    ordering_fields = (
        "id",
        "competition",
        "user",
        "participant_name",
        "score",
        "disqualified",
        "computed_rank",
    )
    search_fields = ("participant_name",)
    filterset_fields = ("competition", "user", "disqualified")

    def get_queryset(self) -> QuerySet[CompetitionParticipation]:
        """Filter participations by event from URL."""
        event_id = int(self.kwargs["event_pk"])
        return self.queryset.filter(competition__event_id=event_id).select_related("competition").with_rank()

    def validate_competition_belongs_to_event(self, competition: Competition) -> None:
        """Validate that the competition belongs to the event from the URL."""
        event_id = int(self.kwargs["event_pk"])
        if competition.event_id != event_id:
            raise serializers.ValidationError({"competition": ["Competition does not belong to this event"]})

    def _refresh_with_annotations(self, serializer: BaseSerializer[CompetitionParticipation]) -> None:
        """Refresh the serializer instance with rank annotation."""
        assert serializer.instance is not None
        serializer.instance = self.get_queryset().get(pk=serializer.instance.pk)

    def perform_create(self, serializer: BaseSerializer[CompetitionParticipation]) -> None:  # type: ignore[override]
        """Validate competition belongs to event before creating."""
        if competition := serializer.validated_data.get("competition"):
            self.validate_competition_belongs_to_event(competition)
        super().perform_create(serializer)  # type: ignore[arg-type]
        self._refresh_with_annotations(serializer)

    def perform_update(self, serializer: BaseSerializer[CompetitionParticipation]) -> None:  # type: ignore[override]
        assert serializer.instance is not None
        if new_competition := serializer.validated_data.get("competition"):
            if new_competition.id != serializer.instance.competition_id:
                raise serializers.ValidationError(
                    {"competition": ["Cannot change competition after creation"]}
                )
        super().perform_update(serializer)  # type: ignore[arg-type]
        self._refresh_with_annotations(serializer)
