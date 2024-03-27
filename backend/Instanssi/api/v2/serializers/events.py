from rest_framework.serializers import ModelSerializer

from Instanssi.kompomaatti.models import Event


class EventSerializer(ModelSerializer):
    class Meta:
        model = Event
        fields = ("id", "name", "tag", "date", "archived", "mainurl")
        read_only_fields = ("id",)
