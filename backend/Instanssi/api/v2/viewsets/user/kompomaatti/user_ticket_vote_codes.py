from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers
from rest_framework.filters import OrderingFilter
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import GenericViewSet

from Instanssi.api.v2.serializers.user.kompomaatti.user_ticket_vote_code_serializer import (
    UserTicketVoteCodeSerializer,
)
from Instanssi.kompomaatti.models import Event, TicketVoteCode
from Instanssi.store.models import TransactionItem


class UserTicketVoteCodeViewSet(
    CreateModelMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet[TicketVoteCode]
):
    """
    API endpoint for managing user's own ticket vote codes.

    Users can associate a ticket key (from their purchase) to their account to gain voting rights.
    This is a create/read-only endpoint - users cannot update or delete their vote codes.

    To create a vote code, POST with:
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

    @transaction.atomic
    def perform_create(self, serializer: BaseSerializer[TicketVoteCode]) -> None:
        """Validate ticket key against the event and create vote code."""
        event_id = int(self.kwargs["event_pk"])
        event = Event.objects.filter(id=event_id).first()
        if not event:
            raise serializers.ValidationError({"event": ["Event not found."]})

        user: User = self.request.user  # type: ignore[assignment]

        if TicketVoteCode.objects.filter(event=event, associated_to=user).exists():
            raise serializers.ValidationError(
                {"non_field_errors": ["You already have a vote code for this event"]}
            )

        ticket_key: str = serializer.validated_data.pop("ticket_key")

        if TicketVoteCode.objects.filter(event=event, ticket__key__startswith=ticket_key).exists():
            raise serializers.ValidationError({"ticket_key": ["This ticket key has already been used."]})

        try:
            ticket = TransactionItem.objects.get(
                item__event=event,
                item__is_ticket=True,
                key__startswith=ticket_key,
                transaction__time_paid__isnull=False,
            )
        except TransactionItem.DoesNotExist:
            raise serializers.ValidationError({"ticket_key": ["No valid ticket found with this key."]})
        except TransactionItem.MultipleObjectsReturned:
            raise serializers.ValidationError(
                {"ticket_key": ["Ticket key is ambiguous. Please provide more characters."]}
            )

        serializer.save(event=event, ticket=ticket, associated_to=user, time=timezone.now())
