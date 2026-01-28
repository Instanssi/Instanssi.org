from typing import Any

from rest_framework.serializers import ModelSerializer, ValidationError

from Instanssi.kompomaatti.models import VoteCodeRequest


class UserVoteCodeRequestSerializer(ModelSerializer[VoteCodeRequest]):
    """Serializer for user's own vote code requests.

    Users can create and read their own vote code requests.
    The status field is read-only for users (only staff can change it).
    The event is set from the URL, not from the request body.

    Status values:
    - 0: Pending
    - 1: Accepted (voting right granted)
    - 2: Rejected (no voting right)
    """

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        data = super().validate(data)

        # Get event from instance (for updates) or it will be set in perform_create
        event = self.instance.event if self.instance else None
        if not event:
            # For create, we need to get event_pk from view kwargs
            view = self.context.get("view")
            if view and hasattr(view, "kwargs"):
                from Instanssi.kompomaatti.models import Event

                event_pk = view.kwargs.get("event_pk")
                if event_pk:
                    event = Event.objects.filter(id=event_pk).first()

        if not event:
            raise ValidationError({"event": ["Could not determine event from URL."]})

        # Check for duplicate request per event (only for new instances)
        request = self.context.get("request")
        if request and request.user and not self.instance:
            existing = VoteCodeRequest.objects.filter(event=event, user=request.user).first()
            if existing:
                raise ValidationError(
                    {"non_field_errors": ["You have already requested a vote code for this event"]}
                )

        return data

    class Meta:
        model = VoteCodeRequest
        fields = ("id", "event", "text", "status")
        extra_kwargs = {
            "id": {"read_only": True},
            "event": {"read_only": True},  # Set from URL, not request body
            "text": {"required": True},
            "status": {"read_only": True},
        }
