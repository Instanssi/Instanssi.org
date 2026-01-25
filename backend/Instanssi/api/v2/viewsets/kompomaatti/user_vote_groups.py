from django.contrib.auth.models import User
from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers
from rest_framework.filters import OrderingFilter
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import GenericViewSet

from Instanssi.api.v2.serializers.kompomaatti.user_vote_group_serializer import (
    UserVoteGroupSerializer,
)
from Instanssi.kompomaatti.models import Compo, VoteGroup


class UserVoteGroupViewSet(CreateModelMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet[VoteGroup]):
    """
    API endpoint for managing user's votes.

    Users submit a ranked list of entries to vote for a compo.
    The order of entries in the list determines the ranking (first = highest rank).

    To vote, POST with:
    - compo: The compo ID
    - entries: List of entry IDs in order of preference

    Re-submitting votes for the same compo replaces previous votes.
    Users can only vote if they have voting rights (TicketVoteCode or approved VoteCodeRequest).
    Votes can only be submitted while the compo voting is open.

    Note: Update and delete are not supported. To change votes, simply POST again.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserVoteGroupSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    ordering_fields = ("id", "compo")
    filterset_fields = ("compo",)

    def get_queryset(self) -> QuerySet[VoteGroup]:
        """Return only the current user's vote groups for compos in this event."""
        event_id = int(self.kwargs["event_pk"])
        user: User = self.request.user  # type: ignore[assignment]
        return VoteGroup.objects.filter(compo__event_id=event_id, user=user)

    def validate_compo_belongs_to_event(self, compo: Compo) -> None:
        """Validate that compo belongs to the event in the URL."""
        event_id = int(self.kwargs["event_pk"])
        if compo.event_id != event_id:
            raise serializers.ValidationError({"compo": ["Compo does not belong to this event"]})

    def perform_create(self, serializer: BaseSerializer[VoteGroup]) -> None:
        """Create vote group with the current user."""
        if compo := serializer.validated_data.get("compo"):
            self.validate_compo_belongs_to_event(compo)
        serializer.save(user=self.request.user)
