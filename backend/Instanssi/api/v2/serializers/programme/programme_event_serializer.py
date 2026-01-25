from rest_framework.serializers import ModelSerializer, SerializerMethodField

from Instanssi.ext_programme.models import ProgrammeEvent


class ProgrammeEventSerializer(ModelSerializer[ProgrammeEvent]):
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
            "icon_original",
            "icon_small_url",
            "icon2_original",
            "icon2_small_url",
            "email",
            "home_url",
            "twitter_url",
            "github_url",
            "facebook_url",
            "linkedin_url",
            "wiki_url",
            "event_type",
            "active",
        )
        read_only_fields = ("event",)  # Set from URL, not request body

    def get_icon_small_url(self, obj: ProgrammeEvent) -> str | None:
        """Return URL for small icon thumbnail, or None if no icon exists."""
        if obj.icon_original:
            return str(obj.icon_small.url)
        return None

    def get_icon2_small_url(self, obj: ProgrammeEvent) -> str | None:
        """Return URL for small icon2 thumbnail, or None if no icon2 exists."""
        if obj.icon2_original:
            return str(obj.icon2_small.url)
        return None
