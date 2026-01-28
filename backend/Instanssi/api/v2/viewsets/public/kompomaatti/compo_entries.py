from django.db.models import QuerySet
from django.utils import timezone

from Instanssi.api.v2.serializers.public.kompomaatti import PublicCompoEntrySerializer
from Instanssi.api.v2.utils.base import PublicReadOnlyViewSet
from Instanssi.kompomaatti.models import Entry


class PublicCompoEntryViewSet(PublicReadOnlyViewSet[Entry]):
    """Public read-only endpoint for compo entries.

    Only entries from active compos where voting has started are shown.
    """

    serializer_class = PublicCompoEntrySerializer

    def get_queryset(self) -> QuerySet[Entry]:
        event_id = int(self.kwargs["event_pk"])
        return (
            Entry.objects.filter(
                compo__event_id=event_id,
                compo__active=True,
                compo__voting_start__lte=timezone.now(),
            )
            .select_related("compo")
            .prefetch_related("alternate_files")
        )
