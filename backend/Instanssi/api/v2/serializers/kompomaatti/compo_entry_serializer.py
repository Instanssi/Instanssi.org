from typing import Optional

from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from Instanssi.kompomaatti.models import Entry

from .alternate_entry_file_serializer import AlternateEntryFileSerializer


class CompoEntrySerializer(ModelSerializer):
    entryfile_url = SerializerMethodField()
    sourcefile_url = SerializerMethodField()
    imagefile_original_url = SerializerMethodField()
    imagefile_thumbnail_url = SerializerMethodField()
    imagefile_medium_url = SerializerMethodField()
    rank = SerializerMethodField()
    score = SerializerMethodField()
    alternate_files = AlternateEntryFileSerializer(many=True, read_only=True)

    def get_entryfile_url(self, obj: Entry) -> Optional[str]:
        if obj.entryfile:
            return self.context["request"].build_absolute_uri(obj.entryfile.url)
        return None

    def get_sourcefile_url(self, obj: Entry) -> Optional[str]:
        if obj.sourcefile:
            return self.context["request"].build_absolute_uri(obj.sourcefile.url)
        return None

    def get_imagefile_original_url(self, obj: Entry) -> Optional[str]:
        if obj.imagefile_original:
            return self.context["request"].build_absolute_uri(obj.imagefile_original.url)
        return None

    def get_imagefile_medium_url(self, obj: Entry) -> Optional[str]:
        if obj.imagefile_medium:
            return self.context["request"].build_absolute_uri(obj.imagefile_medium.url)
        return None

    def get_imagefile_thumbnail_url(self, obj: Entry) -> Optional[str]:
        if obj.imagefile_thumbnail:
            return self.context["request"].build_absolute_uri(obj.imagefile_thumbnail.url)
        return None

    def get_rank(self, obj: Entry) -> Optional[int]:
        # Show rank only if user has permissions or show_voting_results is enabled
        request = self.context.get("request")
        if request and request.user.is_authenticated and request.user.has_perm("kompomaatti.view_entry"):
            return obj.get_rank()
        if obj.compo.show_voting_results:
            return obj.get_rank()
        return None

    def get_score(self, obj: Entry) -> Optional[float]:
        # Show score only if user has permissions or show_voting_results is enabled
        request = self.context.get("request")
        if request and request.user.is_authenticated and request.user.has_perm("kompomaatti.view_entry"):
            return obj.get_score()
        if obj.compo.show_voting_results:
            return obj.get_score()
        return None

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
