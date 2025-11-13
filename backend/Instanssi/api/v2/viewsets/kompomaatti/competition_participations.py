from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination

from Instanssi.api.v2.serializers.kompomaatti import CompetitionParticipationSerializer
from Instanssi.api.v2.utils.base import PermissionViewSet
from Instanssi.kompomaatti.models import CompetitionParticipation


class CompetitionParticipationViewSet(PermissionViewSet):
    queryset = CompetitionParticipation.objects.all()
    serializer_class = CompetitionParticipationSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    ordering_fields = ("id", "competition", "user", "score")
    filterset_fields = ("competition", "user", "disqualified")

    def get_queryset(self):
        """Filter participations by event from URL"""
        event_id = self.kwargs.get("event_pk")
        return self.queryset.filter(competition__event_id=event_id)
