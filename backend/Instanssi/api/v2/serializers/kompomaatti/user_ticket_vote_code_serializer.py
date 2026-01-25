from typing import Any

from django.db import transaction
from django.utils import timezone
from rest_framework.serializers import CharField, ModelSerializer, ValidationError

from Instanssi.kompomaatti.models import Event, TicketVoteCode
from Instanssi.store.models import TransactionItem


class UserTicketVoteCodeSerializer(ModelSerializer[TicketVoteCode]):
    """Serializer for user's own ticket vote codes.

    Users associate a ticket key (from their purchase) to their account to gain voting rights.
    The ticket_key field accepts a partial key (at least 8 characters) to find the matching ticket.
    The event is set from the URL, not from the request body.

    This is a create/read-only endpoint - users cannot update or delete their vote codes.
    """

    ticket_key = CharField(min_length=8, write_only=True, trim_whitespace=True)

    def _get_event_from_url(self) -> Event | None:
        """Get the event from the URL kwargs."""
        view = self.context.get("view")
        if view and hasattr(view, "kwargs"):
            event_pk = view.kwargs.get("event_pk")
            if event_pk:
                return Event.objects.filter(id=event_pk).first()
        return None

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        data = super().validate(data)

        event = self._get_event_from_url()
        if not event:
            raise ValidationError({"event": ["Could not determine event from URL."]})

        # Store event for use in create()
        data["_event"] = event

        request = self.context.get("request")
        if not request or not request.user:
            raise ValidationError({"non_field_errors": ["Authentication required"]})

        # Check if user already has a vote code for this event
        existing = TicketVoteCode.objects.filter(event=event, associated_to=request.user).first()
        if existing:
            raise ValidationError({"non_field_errors": ["You already have a vote code for this event"]})

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
    def create(self, validated_data: dict[str, Any]) -> TicketVoteCode:
        ticket = validated_data.pop("_ticket")
        event = validated_data.pop("_event")
        validated_data.pop("ticket_key", None)

        instance = TicketVoteCode.objects.create(
            event=event,
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
            "event": {"read_only": True},  # Set from URL, not request body
            "time": {"read_only": True},
        }
