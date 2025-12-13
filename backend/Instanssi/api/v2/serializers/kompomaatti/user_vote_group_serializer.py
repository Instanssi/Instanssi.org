from typing import List

from django.db import transaction
from rest_framework.serializers import (
    ListField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    SerializerMethodField,
    ValidationError,
)

from Instanssi.kompomaatti.models import (
    Entry,
    TicketVoteCode,
    VoteCodeRequest,
    VoteGroup,
)


class UserVoteGroupSerializer(ModelSerializer):
    """Serializer for user's votes in a compo.

    Users submit a ranked list of entries to vote for.
    The order of entries in the list determines the ranking (first = highest rank).
    Re-submitting votes replaces previous votes for the same compo.
    """

    entries = ListField(
        min_length=1,
        child=PrimaryKeyRelatedField(queryset=Entry.objects.filter(compo__active=True, disqualified=False)),
        write_only=True,
        help_text="List of entry IDs in order of preference (first = highest rank)",
    )
    voted_entries = SerializerMethodField(read_only=True)

    def get_voted_entries(self, obj: VoteGroup) -> List[int]:
        """Return the list of entry IDs in ranked order."""
        return [entry.id for entry in obj.entries]

    def validate_entries(self, entries: List[Entry]) -> List[Entry]:
        # Fail if not unique entries
        ids = [entry.id for entry in entries]
        if len(ids) > len(set(ids)):
            raise ValidationError("You can only vote for each entry once")
        return entries

    def validate_compo(self, compo):
        # Make sure compo is scoped to the event from the URL
        view = self.context.get("view")
        if view and hasattr(view, "kwargs"):
            event_pk = view.kwargs.get("event_pk")
            if event_pk and compo.event_id != event_pk:
                raise ValidationError("Compo does not belong to this event")
        return compo

    def validate(self, data: dict) -> dict:
        data = super().validate(data)

        compo = data.get("compo")
        if not compo:
            raise ValidationError({"compo": ["This field is required."]})

        entries = data.get("entries", [])
        request = self.context.get("request")
        if not request or not request.user:
            raise ValidationError("Authentication required")

        user = request.user

        # Make sure compo voting is open
        if not compo.is_voting_open():
            raise ValidationError("Voting is not open for this compo")

        # Make sure user has rights to vote
        has_ticket_code = TicketVoteCode.objects.filter(associated_to=user, event=compo.event).exists()
        has_approved_request = VoteCodeRequest.objects.filter(
            user=user, event=compo.event, status=1
        ).exists()
        if not has_ticket_code and not has_approved_request:
            raise ValidationError("You do not have voting rights for this event")

        # Make sure all entries belong to the requested compo
        for entry in entries:
            if entry.compo_id != compo.id:
                raise ValidationError(
                    {"entries": [f"Entry '{entry.name}' does not belong to compo '{compo.name}'"]}
                )

        return data

    @transaction.atomic
    def create(self, validated_data: dict) -> VoteGroup:
        entries = validated_data.pop("entries")
        compo = validated_data["compo"]
        user = validated_data["user"]

        # Delete old votes (if any) and add new ones
        group = VoteGroup.objects.filter(compo=compo, user=user).first()
        if group:
            group.delete_votes()
        else:
            group = VoteGroup.objects.create(compo=compo, user=user)

        # Add new voted entries
        group.create_votes(entries)

        return group

    class Meta:
        model = VoteGroup
        fields = ("id", "compo", "entries", "voted_entries")
        extra_kwargs = {
            "id": {"read_only": True},
            "compo": {"required": True},
        }
