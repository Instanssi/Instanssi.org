from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination

from Instanssi.api.v2.serializers.kompomaatti import VoteCodeRequestSerializer
from Instanssi.api.v2.utils.base import PermissionViewSet
from Instanssi.kompomaatti.models import VoteCodeRequest


class VoteCodeRequestViewSet(PermissionViewSet):
    queryset = VoteCodeRequest.objects.all()
    serializer_class = VoteCodeRequestSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    ordering_fields = ("id", "event", "user", "status")
    filterset_fields = ("user", "status")

    def get_queryset(self):
        """Filter vote code requests by event from URL"""
        event_id = self.kwargs.get("event_pk")
        return self.queryset.filter(event_id=event_id)
