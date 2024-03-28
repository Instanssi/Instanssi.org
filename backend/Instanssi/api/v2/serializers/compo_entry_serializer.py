from typing import Optional

from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from Instanssi.api.v1.serializers.kompomaatti import AlternateEntryFileSerializer
from Instanssi.kompomaatti.models import Entry


class CompoEntrySerializer(ModelSerializer):
    entry_file_url = SerializerMethodField()
    source_file_url = SerializerMethodField()
    image_file_original_url = SerializerMethodField()
    image_file_thumbnail_url = SerializerMethodField()
    image_file_medium_url = SerializerMethodField()
    rank = SerializerMethodField()
    score = SerializerMethodField()
    youtube_url = SerializerMethodField()
    disqualified = SerializerMethodField()
    disqualified_reason = SerializerMethodField()
    alternate_files = AlternateEntryFileSerializer(many=True, read_only=True)

    def get_entry_file_url(self, obj: Entry) -> Optional[str]:
        if obj.entryfile and (obj.compo.show_voting_results or obj.compo.has_voting_started):
            return self.context["request"].build_absolute_uri(obj.entryfile.url)
        return None

    def get_source_file_url(self, obj: Entry) -> Optional[str]:
        if obj.sourcefile and (obj.compo.show_voting_results or obj.compo.has_voting_started):
            return self.context["request"].build_absolute_uri(obj.sourcefile.url)
        return None

    def get_image_file_original_url(self, obj: Entry) -> Optional[str]:
        if obj.imagefile_original:
            return self.context["request"].build_absolute_uri(obj.imagefile_original.url)
        return None

    def get_image_file_medium_url(self, obj: Entry) -> Optional[str]:
        if obj.imagefile_medium:
            return self.context["request"].build_absolute_uri(obj.imagefile_medium.url)
        return None

    def get_image_file_thumbnail_url(self, obj: Entry) -> Optional[str]:
        if obj.imagefile_thumbnail:
            return self.context["request"].build_absolute_uri(obj.imagefile_thumbnail.url)
        return None

    def get_disqualified_reason(self, obj: Entry) -> Optional[str]:
        if obj.compo.has_voting_started():
            return obj.disqualified_reason
        return None

    def get_disqualified(self, obj: Entry) -> Optional[bool]:
        if obj.compo.has_voting_started():
            return obj.disqualified
        return None

    def get_rank(self, obj: Entry) -> Optional[int]:
        if obj.compo.show_voting_results:
            return obj.get_rank()
        return None

    def get_score(self, obj: Entry) -> Optional[float]:
        if obj.compo.show_voting_results:
            return obj.get_score()
        return None

    def get_youtube_url(self, obj: Entry) -> Optional[str]:
        if obj.youtube_url:
            return obj.youtube_url.link_url
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
            "entry_file_url",
            "source_file_url",
            "image_file_original_url",
            "image_file_thumbnail_url",
            "image_file_medium_url",
            "youtube_url",
            "disqualified",
            "disqualified_reason",
            "score",
            "rank",
            "alternate_files",
        )
        extra_kwargs = {}
