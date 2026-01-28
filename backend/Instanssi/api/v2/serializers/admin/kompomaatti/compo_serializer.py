from rest_framework.fields import CharField, IntegerField, ListField
from rest_framework.serializers import ModelSerializer

from Instanssi.kompomaatti.models import Compo


class CompoSerializer(ModelSerializer[Compo]):
    """Staff serializer for compos."""

    max_entry_size = IntegerField(read_only=True)
    max_source_size = IntegerField(read_only=True)
    source_format_list = ListField(child=CharField(), read_only=True)
    entry_format_list = ListField(child=CharField(), read_only=True)
    image_format_list = ListField(child=CharField(), read_only=True)

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
            "entry_sizelimit",
            "source_sizelimit",
            "formats",
            "source_formats",
            "image_formats",
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
        read_only_fields = ("event",)  # Set from URL, not request body
