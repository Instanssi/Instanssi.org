from django.db.models import QuerySet
from django.utils import timezone

from Instanssi.api.v2.serializers.public.kompomaatti import (
    PublicCompetitionParticipationSerializer,
)
from Instanssi.api.v2.utils.base import PublicReadOnlyViewSet
from Instanssi.kompomaatti.models import CompetitionParticipation


class PublicCompetitionParticipationViewSet(PublicReadOnlyViewSet[CompetitionParticipation]):
    """Public read-only endpoint for competition participations.

    Only participations from active competitions that have started are shown.
    """

    serializer_class = PublicCompetitionParticipationSerializer
    queryset = CompetitionParticipation.objects.all()

    def get_queryset(self) -> QuerySet[CompetitionParticipation]:
        event_id = int(self.kwargs["event_pk"])
        return self.queryset.filter(
            competition__event_id=event_id,
            competition__active=True,
            competition__start__lte=timezone.now(),
        ).select_related("competition")
