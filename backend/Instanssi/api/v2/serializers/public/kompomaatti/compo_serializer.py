from rest_framework.serializers import ModelSerializer

from Instanssi.kompomaatti.models import Compo


class PublicCompoSerializer(ModelSerializer[Compo]):
    class Meta:
        model = Compo
        fields = (
            "id",
            "event",
            "name",
            "description",
            "adding_end",
            "editing_end",
            "compo_start",
            "voting_start",
            "voting_end",
            "entry_view_type",
            "is_votable",
        )
