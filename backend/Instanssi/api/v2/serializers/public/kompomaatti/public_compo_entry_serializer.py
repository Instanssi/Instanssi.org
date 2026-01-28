from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from Instanssi.kompomaatti.models import Entry

from .alternate_entry_file_serializer import PublicAlternateEntryFileSerializer


class PublicCompoEntrySerializer(ModelSerializer[Entry]):
    """Public serializer for compo entries.

    Drops sensitive/staff-only fields: user FK, file upload fields (entryfile, sourcefile,
    imagefile_original), file URL fields (entryfile_url, sourcefile_url),
    disqualified_reason, archive_score, archive_rank.

    Rank/score are shown only when compo.show_voting_results is True.
    """

    imagefile_original_url = SerializerMethodField()
    imagefile_thumbnail_url = SerializerMethodField()
    imagefile_medium_url = SerializerMethodField()
    rank = SerializerMethodField()
    score = SerializerMethodField()
    disqualified = SerializerMethodField()
    disqualified_reason = SerializerMethodField()
    alternate_files = PublicAlternateEntryFileSerializer(many=True, read_only=True)

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
        if obj.compo.show_voting_results:
            return obj.get_rank()
        return None

    def get_score(self, obj: Entry) -> float | None:
        if obj.compo.show_voting_results:
            return obj.get_score()
        return None

    def get_disqualified(self, obj: Entry) -> bool | None:
        if obj.compo.show_voting_results:
            return obj.disqualified
        return None

    def get_disqualified_reason(self, obj: Entry) -> str | None:
        if obj.compo.show_voting_results:
            return obj.disqualified_reason
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
