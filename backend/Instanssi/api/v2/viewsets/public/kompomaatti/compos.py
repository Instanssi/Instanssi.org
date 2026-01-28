from django.db.models import QuerySet

from Instanssi.api.v2.serializers.public.kompomaatti import PublicCompoSerializer
from Instanssi.api.v2.utils.base import PublicReadOnlyViewSet
from Instanssi.kompomaatti.models import Compo


class PublicCompoViewSet(PublicReadOnlyViewSet[Compo]):
    """Public read-only endpoint for compos. Only active compos are shown."""

    serializer_class = PublicCompoSerializer

    def get_queryset(self) -> QuerySet[Compo]:
        event_id = int(self.kwargs["event_pk"])
        return Compo.objects.filter(event_id=event_id, active=True)
