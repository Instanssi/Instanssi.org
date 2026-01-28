from rest_framework.serializers import ModelSerializer, SerializerMethodField

from Instanssi.ext_programme.models import ProgrammeEvent


class PublicProgramEventSerializer(ModelSerializer[ProgrammeEvent]):
    icon_small_url = SerializerMethodField()
    icon2_small_url = SerializerMethodField()

    class Meta:
        model = ProgrammeEvent
        fields = (
            "id",
            "event",
            "start",
            "end",
            "title",
            "description",
            "presenters",
            "presenters_titles",
            "place",
            "icon_small_url",
            "icon2_small_url",
            "home_url",
            "twitter_url",
            "github_url",
            "facebook_url",
            "linkedin_url",
            "wiki_url",
            "event_type",
        )

    def get_icon_small_url(self, obj: ProgrammeEvent) -> str | None:
        if obj.icon_original:
            return str(obj.icon_small.url)
        return None

    def get_icon2_small_url(self, obj: ProgrammeEvent) -> str | None:
        if obj.icon2_original:
            return str(obj.icon2_small.url)
        return None
