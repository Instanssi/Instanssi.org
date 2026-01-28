from rest_framework.serializers import ModelSerializer

from Instanssi.kompomaatti.models import Event


class PublicEventSerializer(ModelSerializer[Event]):
    class Meta:
        model = Event
        fields = ("id", "name", "tag", "date", "archived", "mainurl")
