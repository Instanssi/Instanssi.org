from Instanssi.api.v2.serializers.admin.events import EventSerializer
from Instanssi.api.v2.utils.base import PermissionViewSet
from Instanssi.kompomaatti.models import Event


class EventViewSet(PermissionViewSet):
    """Staff viewset for managing events."""

    queryset = Event.objects.all()
    serializer_class = EventSerializer  # type: ignore[assignment]
    ordering_fields = ("id", "name", "date", "tag")
    search_fields = ("name", "tag")
