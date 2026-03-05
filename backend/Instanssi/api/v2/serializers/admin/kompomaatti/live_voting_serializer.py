from typing import Any

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework.utils.serializer_helpers import ReturnDict

from Instanssi.kompomaatti.models import Entry, LiveVotingState


class LiveVotingEntrySerializer(ModelSerializer[Entry]):
    imagefile_thumbnail_url = SerializerMethodField()

    def get_imagefile_thumbnail_url(self, obj: Entry) -> str | None:
        if obj.imagefile_thumbnail:
            return str(self.context["request"].build_absolute_uri(obj.imagefile_thumbnail.url))
        return None

    class Meta:
        model = Entry
        fields = (
            "id",
            "name",
            "creator",
            "imagefile_thumbnail_url",
            "live_voting_revealed",
            "live_voting_order",
        )
        read_only_fields = fields


class LiveVotingStateSerializer(ModelSerializer[LiveVotingState]):
    entries = SerializerMethodField()

    @extend_schema_field(LiveVotingEntrySerializer(many=True))
    def get_entries(self, obj: LiveVotingState) -> ReturnDict[Any, Any]:
        entries = Entry.objects.filter(compo=obj.compo).order_by(
            "-live_voting_revealed", "live_voting_order", "id"
        )
        return LiveVotingEntrySerializer(entries, many=True, context=self.context).data

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
