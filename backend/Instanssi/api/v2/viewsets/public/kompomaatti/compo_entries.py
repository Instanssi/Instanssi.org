from django.db.models import Q, QuerySet
from django.utils import timezone

from Instanssi.api.v2.serializers.public.kompomaatti import PublicCompoEntrySerializer
from Instanssi.api.v2.utils.base import PublicReadOnlyViewSet
from Instanssi.kompomaatti.models import Entry


class PublicCompoEntryViewSet(PublicReadOnlyViewSet[Entry]):
    """Public read-only endpoint for compo entries.

    Only entries from active compos where voting has started (or the event
    is archived) are shown.
    """

    serializer_class = PublicCompoEntrySerializer
    queryset = Entry.objects.all()

    def get_queryset(self) -> QuerySet[Entry]:
        event_id = int(self.kwargs["event_pk"])
        return (
            self.queryset.filter(
                compo__event_id=event_id,
                compo__active=True,
            )
            .filter(Q(compo__voting_start__lte=timezone.now()) | Q(compo__event__archived=True))
            .select_related("compo")
            .prefetch_related("alternate_files")
        )
