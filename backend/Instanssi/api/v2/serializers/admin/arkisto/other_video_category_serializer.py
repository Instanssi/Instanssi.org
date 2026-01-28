from rest_framework.serializers import ModelSerializer

from Instanssi.arkisto.models import OtherVideoCategory


class OtherVideoCategorySerializer(ModelSerializer[OtherVideoCategory]):
    class Meta:
        model = OtherVideoCategory
        fields = (
            "id",
            "event",
            "name",
        )
        read_only_fields = ("event",)  # Set from URL, not request body
