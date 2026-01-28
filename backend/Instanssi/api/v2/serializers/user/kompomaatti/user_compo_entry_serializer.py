from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from Instanssi.api.v2.serializers.admin.kompomaatti.alternate_entry_file_serializer import (
    AlternateEntryFileSerializer,
)
from Instanssi.kompomaatti.models import Entry


class UserCompoEntrySerializer(ModelSerializer[Entry]):
    """User serializer for managing own compo entries."""

    entryfile_url = SerializerMethodField()
    sourcefile_url = SerializerMethodField()
    imagefile_original_url = SerializerMethodField()
    imagefile_thumbnail_url = SerializerMethodField()
    imagefile_medium_url = SerializerMethodField()
    rank = SerializerMethodField()
    score = SerializerMethodField()
    youtube_url = SerializerMethodField()
    disqualified = SerializerMethodField()
    disqualified_reason = SerializerMethodField()
    alternate_files = AlternateEntryFileSerializer(many=True, read_only=True)

    def get_entryfile_url(self, obj: Entry) -> str | None:
        # User can always see their own entry files
        if obj.entryfile:
            return str(self.context["request"].build_absolute_uri(obj.entryfile.url))
        return None

    def get_sourcefile_url(self, obj: Entry) -> str | None:
        # User can always see their own source files
        if obj.sourcefile:
            return str(self.context["request"].build_absolute_uri(obj.sourcefile.url))
        return None

    def get_imagefile_original_url(self, obj: Entry) -> str | None:
        if obj.imagefile_original:
            return str(self.context["request"].build_absolute_uri(obj.imagefile_original.url))
        return None

    def get_imagefile_medium_url(self, obj: Entry) -> str | None:
        if obj.imagefile_medium:
            return str(self.context["request"].build_absolute_uri(obj.imagefile_medium.url))
        return None

    def get_imagefile_thumbnail_url(self, obj: Entry) -> str | None:
        if obj.imagefile_thumbnail:
            return str(self.context["request"].build_absolute_uri(obj.imagefile_thumbnail.url))
        return None

    def get_disqualified_reason(self, obj: Entry) -> str | None:
        if obj.compo.has_voting_started():
            return obj.disqualified_reason
        return None

    def get_disqualified(self, obj: Entry) -> bool | None:
        if obj.compo.has_voting_started():
            return obj.disqualified
        return None

    def get_rank(self, obj: Entry) -> int | None:
        if obj.compo.show_voting_results:
            return obj.get_rank()
        return None

    def get_score(self, obj: Entry) -> float | None:
        if obj.compo.show_voting_results:
            return obj.get_score()
        return None

    def get_youtube_url(self, obj: Entry) -> str | None:
        if obj.youtube_url:
            return str(obj.youtube_url.link_url)
        return None

    class Meta:
        model = Entry
        fields = (
            "id",
            "compo",
            "name",
            "description",
            "creator",
            "platform",
            "entryfile",
            "sourcefile",
            "imagefile_original",
            "entryfile_url",
            "sourcefile_url",
            "imagefile_original_url",
            "imagefile_thumbnail_url",
            "imagefile_medium_url",
            "youtube_url",
            "disqualified",
            "disqualified_reason",
            "score",
            "rank",
            "alternate_files",
        )
        extra_kwargs = {
            "id": {"read_only": True},
            "entryfile": {"write_only": True, "required": False},
            "sourcefile": {"write_only": True, "required": False},
            "imagefile_original": {"write_only": True, "required": False},
        }
