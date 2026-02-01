from rest_framework.serializers import ModelSerializer

from Instanssi.kompomaatti.models import Event


class EventSerializer(ModelSerializer[Event]):
    """Staff serializer for events."""

    class Meta:
        model = Event
        fields = ("id", "name", "tag", "date", "archived", "hidden", "mainurl")
        read_only_fields = ("id",)
