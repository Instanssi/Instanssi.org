from django.db.models import QuerySet

from Instanssi.api.v2.serializers.public.program import PublicProgramEventSerializer
from Instanssi.api.v2.utils.base import PublicReadOnlyViewSet
from Instanssi.ext_programme.models import ProgrammeEvent


class PublicProgramEventViewSet(PublicReadOnlyViewSet[ProgrammeEvent]):
    """Public read-only endpoint for program events. Only active events are shown."""

    serializer_class = PublicProgramEventSerializer

    def get_queryset(self) -> QuerySet[ProgrammeEvent]:
        event_id = int(self.kwargs["event_pk"])
        return ProgrammeEvent.objects.filter(event_id=event_id, active=True).order_by("start")
