from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from Instanssi.kompomaatti.models import TicketVoteCode


class TicketVoteCodeSerializer(ModelSerializer[TicketVoteCode]):
    """Staff serializer for ticket vote codes."""

    associated_username = SerializerMethodField()

    def get_associated_username(self, obj: TicketVoteCode) -> str | None:
        return obj.associated_username

    class Meta:
        model = TicketVoteCode
        fields = (
            "id",
            "event",
            "associated_to",
            "ticket",
            "time",
            "associated_username",
        )
        read_only_fields = ("event", "associated_username")
