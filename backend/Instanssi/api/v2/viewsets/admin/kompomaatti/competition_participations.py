from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.serializers import BaseSerializer

from Instanssi.api.v2.serializers.admin.kompomaatti import (
    CompetitionParticipationSerializer,
)
from Instanssi.api.v2.utils.base import PermissionViewSet
from Instanssi.kompomaatti.models import Competition, CompetitionParticipation


class CompetitionParticipationViewSet(PermissionViewSet):
    queryset = CompetitionParticipation.objects.all()
    serializer_class = CompetitionParticipationSerializer  # type: ignore[assignment]
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    ordering_fields = ("id", "competition", "user", "score")
    search_fields = ("participant_name",)
    filterset_fields = ("competition", "user", "disqualified")

    def get_queryset(self) -> QuerySet[CompetitionParticipation]:
        """Filter participations by event from URL."""
        event_id = int(self.kwargs["event_pk"])
        return self.queryset.filter(competition__event_id=event_id).select_related("competition")

    def validate_competition_belongs_to_event(self, competition: Competition) -> None:
        """Validate that the competition belongs to the event from the URL."""
        event_id = int(self.kwargs["event_pk"])
        if competition.event_id != event_id:
            raise serializers.ValidationError({"competition": ["Competition does not belong to this event"]})

    def perform_create(self, serializer: BaseSerializer[CompetitionParticipation]) -> None:  # type: ignore[override]
        """Validate competition belongs to event before creating."""
        if competition := serializer.validated_data.get("competition"):
            self.validate_competition_belongs_to_event(competition)
        super().perform_create(serializer)  # type: ignore[arg-type]

    def perform_update(self, serializer: BaseSerializer[CompetitionParticipation]) -> None:  # type: ignore[override]
        """Validate competition belongs to event if being changed."""
        if competition := serializer.validated_data.get("competition"):
            self.validate_competition_belongs_to_event(competition)
        super().perform_update(serializer)  # type: ignore[arg-type]
