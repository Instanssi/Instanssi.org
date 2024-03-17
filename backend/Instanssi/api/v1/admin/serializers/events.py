from rest_framework.serializers import ModelSerializer

from Instanssi.kompomaatti.models import Event


class AdminEventSerializer(ModelSerializer):
    class Meta:
        model = Event
        fields = ("id", "name", "date", "archived", "mainurl")
        read_only_fields = ("id",)
