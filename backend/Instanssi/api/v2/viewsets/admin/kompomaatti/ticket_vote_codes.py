from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from Instanssi.api.v2.serializers.admin.kompomaatti import TicketVoteCodeSerializer
from Instanssi.api.v2.utils.base import PermissionReadOnlyViewSet
from Instanssi.kompomaatti.models import TicketVoteCode


class TicketVoteCodeViewSet(PermissionReadOnlyViewSet):
    """Staff viewset for viewing ticket vote codes (read-only)."""

    queryset = TicketVoteCode.objects.all()
    serializer_class = TicketVoteCodeSerializer  # type: ignore[assignment]
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    ordering_fields = ("id", "event", "associated_to", "time")
    filterset_fields = ("associated_to", "ticket")

    def get_queryset(self) -> QuerySet[TicketVoteCode]:
        """Filter ticket vote codes by event from URL"""
        event_id = int(self.kwargs["event_pk"])
        return self.queryset.filter(event_id=event_id)
