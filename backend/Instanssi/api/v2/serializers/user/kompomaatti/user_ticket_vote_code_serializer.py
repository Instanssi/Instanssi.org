from rest_framework.serializers import CharField, ModelSerializer

from Instanssi.kompomaatti.models import TicketVoteCode


class UserTicketVoteCodeSerializer(ModelSerializer[TicketVoteCode]):
    """Serializer for user's own ticket vote codes.

    Users associate a ticket key (from their purchase) to their account to gain voting rights.
    The ticket_key field accepts a partial key (at least 8 characters) to find the matching ticket.
    Event, ticket, and associated_to are set by the viewset, not from the request body.
    """

    ticket_key = CharField(min_length=8, write_only=True, trim_whitespace=True)

    class Meta:
        model = TicketVoteCode
        fields = ("id", "event", "time", "ticket_key")
        extra_kwargs = {
            "id": {"read_only": True},
            "event": {"read_only": True},
            "time": {"read_only": True},
        }
