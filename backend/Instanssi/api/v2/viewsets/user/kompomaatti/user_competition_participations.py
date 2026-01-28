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

    def get_queryset(self) -> QuerySet[CompetitionParticipation]:
        """Return only the current user's participations for active competitions in this event."""
        event_id = int(self.kwargs["event_pk"])
        user: User = self.request.user  # type: ignore[assignment]
        return CompetitionParticipation.objects.filter(
            competition__event_id=event_id, competition__active=True, user=user
        ).select_related("competition")

    def validate_competition_belongs_to_event(self, competition: Competition) -> None:
        """Validate that competition belongs to the event in the URL."""
        event_id = int(self.kwargs["event_pk"])
        if competition.event_id != event_id:
            raise serializers.ValidationError({"competition": ["Competition does not belong to this event"]})

    def perform_create(self, serializer: BaseSerializer[CompetitionParticipation]) -> None:
        """Create participation with the current user."""
        if competition := serializer.validated_data.get("competition"):
            self.validate_competition_belongs_to_event(competition)
        serializer.save(user=self.request.user)

    def perform_update(self, serializer: BaseSerializer[CompetitionParticipation]) -> None:
        """Validate that participation can still be modified."""
        instance = serializer.instance
        assert instance is not None  # Always exists in update context
        if not instance.competition.active:
            raise serializers.ValidationError({"competition": ["Competition is not active"]})

        if not instance.competition.is_participating_open():
            raise serializers.ValidationError({"competition": ["Competition participation time has ended"]})

        serializer.save()

    def perform_destroy(self, instance: CompetitionParticipation) -> None:
        """Validate that participation can be deleted."""
        if not instance.competition.active:
            raise serializers.ValidationError({"competition": ["Competition is not active"]})

        if not instance.competition.is_participating_open():
            raise serializers.ValidationError({"competition": ["Competition participation time has ended"]})

        super().perform_destroy(instance)
