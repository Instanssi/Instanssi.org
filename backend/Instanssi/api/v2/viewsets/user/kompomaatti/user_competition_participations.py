from django.contrib.auth.models import User
from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import ModelViewSet

from Instanssi.api.v2.serializers.user.kompomaatti.user_competition_participation_serializer import (
    UserCompetitionParticipationSerializer,
)
from Instanssi.kompomaatti.models import Competition, CompetitionParticipation


class UserCompetitionParticipationViewSet(ModelViewSet[CompetitionParticipation]):
    """
    API endpoint for managing user's own competition participations.

    Users can create, read, update and delete their own participations
    within the allowed time window (before participation_end).
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserCompetitionParticipationSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    ordering_fields = ("id", "competition")
    filterset_fields = ("competition",)
    queryset = CompetitionParticipation.objects.all()

    def get_queryset(self) -> QuerySet[CompetitionParticipation]:
        """Return only the current user's participations for active competitions in this event."""
        event_id = int(self.kwargs["event_pk"])
        user: User = self.request.user  # type: ignore[assignment]
        return self.queryset.filter(
            competition__event_id=event_id, competition__active=True, user=user
        ).select_related("competition")

    def validate_competition_belongs_to_event(self, competition: Competition) -> None:
        """Validate that competition belongs to the event in the URL."""
        event_id = int(self.kwargs["event_pk"])
        if competition.event_id != event_id:
            raise serializers.ValidationError({"competition": ["Competition does not belong to this event"]})

    def validate_competition(self, competition: Competition) -> None:
        """Validate that competition is active and open for participation."""
        if not competition.active:
            raise serializers.ValidationError({"competition": ["Competition is not active"]})

        if not competition.is_participating_open():
            raise serializers.ValidationError({"competition": ["Competition participation time has ended"]})

    def validate_no_duplicate_participation(self, competition: Competition, user: User) -> None:
        """Validate that the user hasn't already participated in this competition."""
        if CompetitionParticipation.objects.filter(competition=competition, user=user).exists():
            raise serializers.ValidationError(
                {"competition": ["You have already participated in this competition"]}
            )

    def perform_create(self, serializer: BaseSerializer[CompetitionParticipation]) -> None:
        """Create participation with the current user."""
        competition: Competition = serializer.validated_data["competition"]
        user: User = self.request.user  # type: ignore[assignment]

        self.validate_competition_belongs_to_event(competition)
        self.validate_competition(competition)
        self.validate_no_duplicate_participation(competition, user)

        serializer.save(user=user)

    def perform_update(self, serializer: BaseSerializer[CompetitionParticipation]) -> None:
        serializer.validated_data.pop("competition", None)
        assert serializer.instance is not None
        self.validate_competition(serializer.instance.competition)
        serializer.save()

    def perform_destroy(self, instance: CompetitionParticipation) -> None:
        """Validate that participation can be deleted."""
        if not instance.competition.active:
            raise serializers.ValidationError({"competition": ["Competition is not active"]})

        if not instance.competition.is_participating_open():
            raise serializers.ValidationError({"competition": ["Competition participation time has ended"]})

        super().perform_destroy(instance)
