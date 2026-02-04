from typing import Optional

from rest_framework.fields import (
    CharField,
    IntegerField,
    ListField,
    SerializerMethodField,
)
from rest_framework.serializers import ModelSerializer

from Instanssi.kompomaatti.models import Compo, Entry


class AdminCompoSerializer(ModelSerializer):
    max_entry_size = IntegerField()
    max_source_size = IntegerField()
    source_format_list = ListField(child=CharField())
    entry_format_list = ListField(child=CharField())
    image_format_list = ListField(child=CharField())

    class Meta:
        model = Compo
        fields = (
            "id",
            "event",
            "name",
            "description",
            "adding_end",
            "editing_end",
            "compo_start",
            "voting_start",
            "voting_end",
            "max_source_size",
            "max_entry_size",
            "source_format_list",
            "entry_format_list",
            "image_format_list",
            "active",
            "show_voting_results",
            "entry_view_type",
            "hide_from_archive",
            "hide_from_frontpage",
            "is_votable",
            "thumbnail_pref",
        )


class AdminCompoEntrySerializer(ModelSerializer):
    entryfile_url = SerializerMethodField()
    sourcefile_url = SerializerMethodField()
    imagefile_original_url = SerializerMethodField()
    imagefile_thumbnail_url = SerializerMethodField()
    imagefile_medium_url = SerializerMethodField()
    rank = SerializerMethodField()
    score = SerializerMethodField()

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

    def get_rank(self, obj: Entry) -> int:
        return obj.computed_rank

    def get_score(self, obj: Entry) -> float:
        return obj.computed_score

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
        )
        extra_kwargs = {
            "entryfile_url": {"read_only": True},
            "sourcefile_url": {"read_only": True},
            "imagefile_original_url": {"read_only": True},
            "imagefile_thumbnail_url": {"read_only": True},
            "imagefile_medium_url": {"read_only": True},
        }
