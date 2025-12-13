from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from Instanssi.api.v2.serializers.kompomaatti.user_competition_participation_serializer import (
    UserCompetitionParticipationSerializer,
)
from Instanssi.kompomaatti.models import CompetitionParticipation


class UserCompetitionParticipationViewSet(ModelViewSet):
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

    def get_queryset(self):
        """Return only the current user's participations for active competitions in this event."""
        event_id = self.kwargs.get("event_pk")
        return CompetitionParticipation.objects.filter(
            competition__event_id=event_id, competition__active=True, user=self.request.user
        )

    def perform_create(self, serializer):
        """Create participation with the current user."""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Validate that participation can still be modified."""
        if not serializer.instance.competition.active:
            raise serializers.ValidationError("Competition is not active")

        if not serializer.instance.competition.is_participating_open():
            raise serializers.ValidationError("Competition participation time has ended")

        serializer.save()

    def perform_destroy(self, instance):
        """Validate that participation can be deleted."""
        if not instance.competition.active:
            raise serializers.ValidationError("Competition is not active")

        if not instance.competition.is_participating_open():
            raise serializers.ValidationError("Competition participation time has ended")

        return super().perform_destroy(instance)
