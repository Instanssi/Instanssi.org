from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.serializers import BaseSerializer

from Instanssi.api.v2.serializers.admin.kompomaatti import TicketVoteCodeSerializer
from Instanssi.api.v2.utils.base import PermissionViewSet
from Instanssi.kompomaatti.models import TicketVoteCode
from Instanssi.store.models import TransactionItem


class TicketVoteCodeViewSet(PermissionViewSet):
    queryset = TicketVoteCode.objects.all()
    serializer_class = TicketVoteCodeSerializer  # type: ignore[assignment]
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    ordering_fields = ("id", "event", "associated_to", "time")
    filterset_fields = ("associated_to", "ticket")

    def get_queryset(self) -> QuerySet[TicketVoteCode]:
        """Filter ticket vote codes by event from URL"""
        event_id = int(self.kwargs["event_pk"])
        return self.queryset.filter(event_id=event_id)

    def validate_ticket_belongs_to_event(self, ticket: TransactionItem) -> None:
        """Validate that ticket belongs to the event in the URL."""
        event_id = int(self.kwargs["event_pk"])
        if ticket.item.event_id != event_id:
            raise serializers.ValidationError({"ticket": ["Ticket does not belong to this event"]})

    def perform_create(self, serializer: BaseSerializer[TicketVoteCode]) -> None:  # type: ignore[override]
        """Set event from URL when creating."""
        if ticket := serializer.validated_data.get("ticket"):
            self.validate_ticket_belongs_to_event(ticket)
        serializer.save(event_id=int(self.kwargs["event_pk"]))
