from django.db import transaction
from django.utils import timezone
from rest_framework.serializers import CharField, ModelSerializer, ValidationError

from Instanssi.kompomaatti.models import TicketVoteCode
from Instanssi.store.models import TransactionItem


class UserTicketVoteCodeSerializer(ModelSerializer):
    """Serializer for user's own ticket vote codes.

    Users associate a ticket key (from their purchase) to their account to gain voting rights.
    The ticket_key field accepts a partial key (at least 8 characters) to find the matching ticket.

    This is a create/read-only endpoint - users cannot update or delete their vote codes.
    """

    ticket_key = CharField(min_length=8, write_only=True, trim_whitespace=True)

    def validate_event(self, event):
        # Make sure event is scoped to the event from the URL
        view = self.context.get("view")
        if view and hasattr(view, "kwargs"):
            event_pk = view.kwargs.get("event_pk")
            if event_pk and event.id != event_pk:
                raise ValidationError("Event does not match URL")
        return event

    def validate(self, data: dict) -> dict:
        data = super().validate(data)

        event = data.get("event")
        if not event:
            raise ValidationError({"event": ["This field is required."]})

        request = self.context.get("request")
        if not request or not request.user:
            raise ValidationError("Authentication required")

        # Check if user already has a vote code for this event
        existing = TicketVoteCode.objects.filter(event=event, associated_to=request.user).first()
        if existing:
            raise ValidationError("You already have a vote code for this event")

        # Validate the ticket key
        ticket_key = data.get("ticket_key")
        if not ticket_key:
            raise ValidationError({"ticket_key": ["This field is required."]})

        # Check if this key is already used for this event
        try:
            TicketVoteCode.objects.get(event=event, ticket__key__startswith=ticket_key)
            raise ValidationError({"ticket_key": ["This ticket key has already been used."]})
        except TicketVoteCode.DoesNotExist:
            pass

        # Check if the ticket exists and is valid
        try:
            ticket = TransactionItem.objects.get(
                item__event=event,
                item__is_ticket=True,
                key__startswith=ticket_key,
                transaction__time_paid__isnull=False,
            )
            # Store the ticket for later use in create()
            data["_ticket"] = ticket
        except TransactionItem.DoesNotExist:
            raise ValidationError({"ticket_key": ["No valid ticket found with this key."]})
        except TransactionItem.MultipleObjectsReturned:
            # Key is too short and matches multiple tickets
            raise ValidationError(
                {"ticket_key": ["Ticket key is ambiguous. Please provide more characters."]}
            )

        return data

    @transaction.atomic
    def create(self, validated_data: dict) -> TicketVoteCode:
        ticket = validated_data.pop("_ticket")
        validated_data.pop("ticket_key", None)

        instance = TicketVoteCode.objects.create(
            event=validated_data["event"],
            associated_to=validated_data["associated_to"],
            ticket=ticket,
            time=timezone.now(),
        )
        return instance

    class Meta:
        model = TicketVoteCode
        fields = ("id", "event", "time", "ticket_key")
        extra_kwargs = {
            "id": {"read_only": True},
            "event": {"required": True},
            "time": {"read_only": True},
        }
