from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from Instanssi.api.v2.utils.youtube_url_field import YoutubeUrlField
from Instanssi.kompomaatti.models import Entry

from .alternate_entry_file_serializer import AlternateEntryFileSerializer


class CompoEntrySerializer(ModelSerializer[Entry]):
    """Staff serializer for compo entries."""

    youtube_url = YoutubeUrlField(required=False, allow_null=True)
    entryfile_url = SerializerMethodField()
    sourcefile_url = SerializerMethodField()
    imagefile_original_url = SerializerMethodField()
    imagefile_thumbnail_url = SerializerMethodField()
    imagefile_medium_url = SerializerMethodField()
    rank = SerializerMethodField()
    score = SerializerMethodField()
    alternate_files = AlternateEntryFileSerializer(many=True, read_only=True)

    def get_entryfile_url(self, obj: Entry) -> str | None:
        if obj.entryfile:
            return str(self.context["request"].build_absolute_uri(obj.entryfile.url))
        return None

    def get_sourcefile_url(self, obj: Entry) -> str | None:
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

    def get_rank(self, obj: Entry) -> int | None:
        return obj.get_rank()

    def get_score(self, obj: Entry) -> float | None:
        return obj.get_score()

    class Meta:
        model = Entry
        fields = (
            "id",
            "user",
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
            "archive_score",
            "archive_rank",
            "score",
            "rank",
            "alternate_files",
        )
        read_only_fields = (
            "entryfile_url",
            "sourcefile_url",
            "imagefile_original_url",
            "imagefile_thumbnail_url",
            "imagefile_medium_url",
            "score",
            "rank",
            "alternate_files",
        )
        extra_kwargs = {
            # allow_null=True lets DRF convert empty string to None for clearing
            "sourcefile": {"required": False, "allow_null": True},
            "imagefile_original": {"required": False, "allow_null": True},
        }
