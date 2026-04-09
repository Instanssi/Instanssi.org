from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer, Serializer

from Instanssi.kompomaatti.models import Entry, LiveVotingState


class LiveVotingEntrySerializer(ModelSerializer[Entry]):
    class Meta:
        model = Entry
        fields = (
            "id",
            "live_voting_revealed",
        )
        read_only_fields = fields


class LiveVotingStateSerializer(ModelSerializer[LiveVotingState]):
    entries = SerializerMethodField()

    @extend_schema_field(LiveVotingEntrySerializer(many=True))
    def get_entries(self, obj: LiveVotingState) -> list[dict[str, object]]:
        entries = Entry.objects.filter(compo=obj.compo).order_by(
            "-live_voting_revealed", "order_index", "id"
        )
        return [{"id": e.id, "live_voting_revealed": e.live_voting_revealed} for e in entries]

    class Meta:
        model = LiveVotingState
        fields = (
            "compo",
            "voting_open",
            "current_entry",
            "updated_at",
            "entries",
        )
        read_only_fields = ("compo", "updated_at", "entries")


class LiveVotingUpdateSerializer(Serializer[None]):
    voting_open = serializers.BooleanField(required=False)
    current_entry = serializers.PrimaryKeyRelatedField(
        queryset=Entry.objects.all(),
        required=False,
        allow_null=True,
    )


class LiveVotingEntryActionSerializer(Serializer[None]):
    entry_id = serializers.IntegerField()
