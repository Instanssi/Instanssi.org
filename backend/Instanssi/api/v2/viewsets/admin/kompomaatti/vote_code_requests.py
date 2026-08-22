from django.db.models import QuerySet
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.serializers import BaseSerializer

from Instanssi.api.v2.serializers.admin.kompomaatti import VoteCodeRequestSerializer
from Instanssi.api.v2.utils.base import PermissionViewSet
from Instanssi.api.v2.utils.filters import ApiFilterBackend
from Instanssi.kompomaatti.models import VoteCodeRequest


class VoteCodeRequestViewSet(PermissionViewSet):
    """Staff viewset for managing vote code requests."""

    queryset = VoteCodeRequest.objects.all()
    serializer_class = VoteCodeRequestSerializer  # type: ignore[assignment]
    filter_backends = (OrderingFilter, SearchFilter, ApiFilterBackend)
    ordering_fields = ("id", "event", "user", "status")
    search_fields = ("user__username", "text")
    filterset_fields = ("user", "status")

    def get_queryset(self) -> QuerySet[VoteCodeRequest]:
        """Filter vote code requests by event from URL"""
        event_id = int(self.kwargs["event_pk"])
        return self.queryset.filter(event_id=event_id)

    def perform_create(self, serializer: BaseSerializer[VoteCodeRequest]) -> None:  # type: ignore[override]
        """Set event from URL when creating."""
        serializer.save(event_id=int(self.kwargs["event_pk"]))
