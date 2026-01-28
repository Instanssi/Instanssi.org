from django.db.models import QuerySet

from Instanssi.api.v2.serializers.public.kompomaatti import PublicCompetitionSerializer
from Instanssi.api.v2.utils.base import PublicReadOnlyViewSet
from Instanssi.kompomaatti.models import Competition


class PublicCompetitionViewSet(PublicReadOnlyViewSet[Competition]):
    """Public read-only endpoint for competitions. Only active competitions are shown."""

    serializer_class = PublicCompetitionSerializer
    queryset = Competition.objects.all()

    def get_queryset(self) -> QuerySet[Competition]:
        event_id = int(self.kwargs["event_pk"])
        return self.queryset.filter(event_id=event_id, active=True)
