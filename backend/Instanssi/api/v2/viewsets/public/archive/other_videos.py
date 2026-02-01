from django.db.models import QuerySet

from Instanssi.api.v2.serializers.public.archive import PublicOtherVideoSerializer
from Instanssi.api.v2.utils.base import PublicReadOnlyViewSet
from Instanssi.arkisto.models import OtherVideo


class PublicOtherVideoViewSet(PublicReadOnlyViewSet[OtherVideo]):
    """Public read-only endpoint for archive videos. Only videos from archived events are shown."""

    serializer_class = PublicOtherVideoSerializer
    queryset = OtherVideo.objects.all()

    def get_queryset(self) -> QuerySet[OtherVideo]:
        event_id = int(self.kwargs["event_pk"])
        return (
            self.queryset.filter(
                category__event_id=event_id,
                category__event__hidden=False,
                category__event__archived=True,
            )
            .select_related("category")
            .order_by("category__name", "name")
        )
