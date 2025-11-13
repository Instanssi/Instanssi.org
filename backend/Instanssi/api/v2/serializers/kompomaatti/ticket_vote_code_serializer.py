from typing import Optional

from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from Instanssi.kompomaatti.models import TicketVoteCode


class TicketVoteCodeSerializer(ModelSerializer):
    key = SerializerMethodField()
    associated_username = SerializerMethodField()

    def get_key(self, obj: TicketVoteCode) -> Optional[str]:
        return obj.key

    def get_associated_username(self, obj: TicketVoteCode) -> Optional[str]:
        return obj.associated_username

    class Meta:
        model = TicketVoteCode
        fields = (
            "id",
            "event",
            "associated_to",
            "ticket",
            "time",
            "key",
            "associated_username",
        )
        read_only_fields = ("key", "associated_username")
