from django.contrib.auth.models import User
from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import GenericViewSet

from Instanssi.api.v2.serializers.kompomaatti.user_ticket_vote_code_serializer import (
    UserTicketVoteCodeSerializer,
)
from Instanssi.kompomaatti.models import TicketVoteCode


class UserTicketVoteCodeViewSet(
    CreateModelMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet[TicketVoteCode]
):
    """
    API endpoint for managing user's own ticket vote codes.

    Users can associate a ticket key (from their purchase) to their account to gain voting rights.
    This is a create/read-only endpoint - users cannot update or delete their vote codes.

    To create a vote code, POST with:
    - event: The event ID
    - ticket_key: At least 8 characters of the ticket key (from purchase receipt)

    The ticket_key must:
    - Match a paid ticket for the specified event
    - Not already be associated with another user
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserTicketVoteCodeSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    ordering_fields = ("id", "event", "time")
    filterset_fields = ("event",)

    def get_queryset(self) -> QuerySet[TicketVoteCode]:
        """Return only the current user's vote codes for this event."""
        event_id = int(self.kwargs["event_pk"])
        user: User = self.request.user  # type: ignore[assignment]
        return TicketVoteCode.objects.filter(event_id=event_id, associated_to=user)

    def perform_create(self, serializer: BaseSerializer[TicketVoteCode]) -> None:
        """Create vote code with the current user."""
        serializer.save(associated_to=self.request.user)
