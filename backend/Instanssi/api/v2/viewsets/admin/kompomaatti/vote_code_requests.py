from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.serializers import BaseSerializer

from Instanssi.api.v2.serializers.admin.kompomaatti import VoteCodeRequestSerializer
from Instanssi.api.v2.utils.base import PermissionViewSet
from Instanssi.kompomaatti.models import VoteCodeRequest


class VoteCodeRequestViewSet(PermissionViewSet):
    queryset = VoteCodeRequest.objects.all()
    serializer_class = VoteCodeRequestSerializer  # type: ignore[assignment]
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    ordering_fields = ("id", "event", "user", "status")
    filterset_fields = ("user", "status")

    def get_queryset(self) -> QuerySet[VoteCodeRequest]:
        """Filter vote code requests by event from URL"""
        event_id = int(self.kwargs["event_pk"])
        return self.queryset.filter(event_id=event_id)

    def perform_create(self, serializer: BaseSerializer[VoteCodeRequest]) -> None:  # type: ignore[override]
        """Set event from URL when creating."""
        serializer.save(event_id=int(self.kwargs["event_pk"]))
