from rest_framework.serializers import ModelSerializer

from Instanssi.kompomaatti.models import VoteCodeRequest


class VoteCodeRequestSerializer(ModelSerializer):
    class Meta:
        model = VoteCodeRequest
        fields = (
            "id",
            "event",
            "user",
            "text",
            "status",
        )
