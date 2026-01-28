from django.db.models import QuerySet

from Instanssi.api.v2.serializers.public.archive import (
    PublicOtherVideoCategorySerializer,
)
from Instanssi.api.v2.utils.base import PublicReadOnlyViewSet
from Instanssi.arkisto.models import OtherVideoCategory


class PublicOtherVideoCategoryViewSet(PublicReadOnlyViewSet[OtherVideoCategory]):
    """Public read-only endpoint for archive video categories.

    Only categories from archived events are shown.
    """

    serializer_class = PublicOtherVideoCategorySerializer

    def get_queryset(self) -> QuerySet[OtherVideoCategory]:
        event_id = int(self.kwargs["event_pk"])
        return OtherVideoCategory.objects.filter(
            event_id=event_id,
            event__archived=True,
        ).order_by("name")
