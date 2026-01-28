from rest_framework.serializers import ModelSerializer

from Instanssi.arkisto.models import OtherVideoCategory


class OtherVideoCategorySerializer(ModelSerializer[OtherVideoCategory]):
    """Staff serializer for archive video categories."""

    class Meta:
        model = OtherVideoCategory
        fields = (
            "id",
            "event",
            "name",
        )
        read_only_fields = ("event",)  # Set from URL, not request body
