from rest_framework.serializers import ModelSerializer, ValidationError

from Instanssi.kompomaatti.models import VoteCodeRequest


class UserVoteCodeRequestSerializer(ModelSerializer):
    """Serializer for user's own vote code requests.

    Users can create and read their own vote code requests.
    The status field is read-only for users (only staff can change it).

    Status values:
    - 0: Pending
    - 1: Accepted (voting right granted)
    - 2: Rejected (no voting right)
    """

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
            if self.instance:
                event = self.instance.event
            else:
                raise ValidationError({"event": ["This field is required."]})

        # Check for duplicate request per event (only for new instances or when changing event)
        request = self.context.get("request")
        if request and request.user:
            has_changed = self.instance and self.instance.event_id != event.id
            if not self.instance or has_changed:
                existing = VoteCodeRequest.objects.filter(event=event, user=request.user).first()
                if existing:
                    raise ValidationError("You have already requested a vote code for this event")

        return data

    class Meta:
        model = VoteCodeRequest
        fields = ("id", "event", "text", "status")
        extra_kwargs = {
            "id": {"read_only": True},
            "event": {"required": True},
            "text": {"required": True},
            "status": {"read_only": True},
        }
