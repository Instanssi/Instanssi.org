from rest_framework.serializers import ModelSerializer

from Instanssi.kompomaatti.models import Event


class PublicEventSerializer(ModelSerializer[Event]):
    """Public read-only serializer for events."""

    class Meta:
        model = Event
        fields = ("id", "name", "tag", "date", "archived", "mainurl")
