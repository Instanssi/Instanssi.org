from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import SAFE_METHODS

from Instanssi.api.v2.serializers.kompomaatti import CompetitionParticipationSerializer
from Instanssi.api.v2.utils.base import FullDjangoModelPermissions, PermissionViewSet
from Instanssi.kompomaatti.models import CompetitionParticipation


class CompetitionParticipationPermissions(FullDjangoModelPermissions):
    """Allow public read access to competition participations after competition has started"""

    def has_permission(self, request, view):
        # Allow public read access (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return True
        # For write operations, require full permissions
        return super().has_permission(request, view)


class CompetitionParticipationViewSet(PermissionViewSet):
    queryset = CompetitionParticipation.objects.all()
    serializer_class = CompetitionParticipationSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    ordering_fields = ("id", "competition", "user", "score")
    filterset_fields = ("competition", "user", "disqualified")
    permission_classes = [CompetitionParticipationPermissions]

    def get_queryset(self):
        """Filter participations by event from URL.

        For non-staff users, only show participations from active competitions where competition has started.
        """
        event_id = self.kwargs.get("event_pk")
        queryset = self.queryset.filter(competition__event_id=event_id)

        # Staff users can see all participations
        if self.request.user.is_authenticated and self.request.user.has_perm(
            "kompomaatti.view_competitionparticipation"
        ):
            return queryset

        # Public users can only see participations from active competitions that have started
        return queryset.filter(competition__active=True, competition__start__lte=timezone.now())
