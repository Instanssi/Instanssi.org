from rest_framework.serializers import ModelSerializer

from Instanssi.kompomaatti.models import VoteCodeRequest


class VoteCodeRequestSerializer(ModelSerializer[VoteCodeRequest]):
    class Meta:
        model = VoteCodeRequest
        fields = (
            "id",
            "event",
            "user",
            "text",
            "status",
        )
        read_only_fields = ("event",)  # Set from URL, not request body
