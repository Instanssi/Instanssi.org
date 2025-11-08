from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination

from Instanssi.api.v2.serializers.kompomaatti import TicketVoteCodeSerializer
from Instanssi.api.v2.utils.base import PermissionViewSet
from Instanssi.kompomaatti.models import TicketVoteCode


class TicketVoteCodeViewSet(PermissionViewSet):
    queryset = TicketVoteCode.objects.all()
    serializer_class = TicketVoteCodeSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    ordering_fields = ("id", "event", "associated_to", "time")
    filterset_fields = ("associated_to", "ticket")

    def get_queryset(self):
        """Filter ticket vote codes by event from URL"""
        event_id = self.kwargs.get("event_pk")
        return self.queryset.filter(event_id=event_id)
