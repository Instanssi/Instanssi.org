from rest_framework.fields import BooleanField, CharField, IntegerField, ListField
from rest_framework.serializers import ModelSerializer

from Instanssi.kompomaatti.models import Compo


class PublicCompoSerializer(ModelSerializer[Compo]):
    """Public read-only serializer for compos."""

    max_entry_size = IntegerField(read_only=True)
    max_source_size = IntegerField(read_only=True)
    max_image_size = IntegerField(read_only=True)
    source_format_list = ListField(child=CharField(), read_only=True)
    entry_format_list = ListField(child=CharField(), read_only=True)
    image_format_list = ListField(child=CharField(), read_only=True)
    is_imagefile_allowed = BooleanField(read_only=True)
    is_imagefile_required = BooleanField(read_only=True)

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
            "voting_end",
            "entry_view_type",
            "max_entry_size",
            "max_source_size",
            "max_image_size",
            "source_format_list",
            "entry_format_list",
            "image_format_list",
            "is_imagefile_allowed",
            "is_imagefile_required",
            "show_voting_results",
        )
        read_only_fields = ("show_voting_results",)
