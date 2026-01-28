from rest_framework.serializers import (
    ListField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    SerializerMethodField,
)

from Instanssi.kompomaatti.models import Entry, VoteGroup


class UserVoteGroupSerializer(ModelSerializer[VoteGroup]):
    """Serializer for user's votes in a compo.

    Users submit a ranked list of entries to vote for.
    The order of entries in the list determines the ranking (first = highest rank).
    Re-submitting votes replaces previous votes for the same compo.
    """

    entries = ListField(
        min_length=1,
        child=PrimaryKeyRelatedField(queryset=Entry.objects.all()),
        write_only=True,
        help_text="List of entry IDs in order of preference (first = highest rank)",
    )
    voted_entries = SerializerMethodField(read_only=True)

    def get_voted_entries(self, obj: VoteGroup) -> list[int]:
        """Return the list of entry IDs in ranked order."""
        return [entry.id for entry in obj.entries]

    class Meta:
        model = VoteGroup
        fields = ("id", "compo", "entries", "voted_entries")
        extra_kwargs = {
            "id": {"read_only": True},
            "compo": {"required": True},
        }
