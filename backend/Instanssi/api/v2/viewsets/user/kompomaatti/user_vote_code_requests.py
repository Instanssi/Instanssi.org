from django.contrib.auth.models import User
from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import GenericViewSet

from Instanssi.api.v2.serializers.user.kompomaatti.user_vote_code_request_serializer import (
    UserVoteCodeRequestSerializer,
)
from Instanssi.kompomaatti.models import VoteCodeRequest


class UserVoteCodeRequestViewSet(
    CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, ListModelMixin, GenericViewSet[VoteCodeRequest]
):
    """
    API endpoint for managing user's own vote code requests.

    Users can create, read, and update their own vote code requests.
    Delete is not supported (requests can only be rejected by staff).

    Status field meanings:
    - 0: Pending
    - 1: Accepted (voting right granted)
    - 2: Rejected (no voting right)

    Note: The status field is read-only for users. Only staff can change it.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserVoteCodeRequestSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    ordering_fields = ("id", "event")
    filterset_fields = ("event", "status")

    def get_queryset(self) -> QuerySet[VoteCodeRequest]:
        """Return only the current user's vote code requests for this event."""
        event_id = int(self.kwargs["event_pk"])
        user: User = self.request.user  # type: ignore[assignment]
        return VoteCodeRequest.objects.filter(event_id=event_id, user=user)

    def perform_create(self, serializer: BaseSerializer[VoteCodeRequest]) -> None:
        """Create vote code request with the current user and event from URL."""
        serializer.save(user=self.request.user, event_id=int(self.kwargs["event_pk"]))
