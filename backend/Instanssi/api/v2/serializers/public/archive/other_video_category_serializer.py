from rest_framework.serializers import ModelSerializer

from Instanssi.arkisto.models import OtherVideoCategory


class PublicOtherVideoCategorySerializer(ModelSerializer[OtherVideoCategory]):
    class Meta:
        model = OtherVideoCategory
        fields = (
            "id",
            "event",
            "name",
        )
