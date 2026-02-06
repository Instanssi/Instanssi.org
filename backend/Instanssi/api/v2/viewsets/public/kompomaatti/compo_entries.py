from django.db.models import Q, QuerySet
from django.utils import timezone
from rest_framework.filters import OrderingFilter

from Instanssi.api.v2.serializers.public.kompomaatti import PublicCompoEntrySerializer
from Instanssi.api.v2.utils.base import PublicReadOnlyViewSet
from Instanssi.kompomaatti.models import Entry


class PublicCompoEntryViewSet(PublicReadOnlyViewSet[Entry]):
    """Public read-only endpoint for compo entries.

    Only entries from active compos where voting has started (or the event
    is archived) are shown.

    Supports ordering by rank and score when results are visible.
    """

    serializer_class = PublicCompoEntrySerializer
    queryset = Entry.objects.all()
    filter_backends = [OrderingFilter]
    ordering_fields = ["id", "name", "compo", "computed_rank", "computed_score"]
    ordering = ["compo", "computed_rank"]

    def get_queryset(self) -> QuerySet[Entry]:
        event_id = int(self.kwargs["event_pk"])
        return (
            self.queryset.filter(
                compo__event_id=event_id,
                compo__event__hidden=False,
                compo__active=True,
            )
            .filter(Q(compo__voting_start__lte=timezone.now()) | Q(compo__event__archived=True))
            .select_related("compo")
            .prefetch_related("alternate_files")
            .with_rank()
        )
