from rest_framework.serializers import ModelSerializer

from Instanssi.api.v2.utils.youtube_url_field import YoutubeUrlField
from Instanssi.arkisto.models import OtherVideo


class PublicOtherVideoSerializer(ModelSerializer[OtherVideo]):
    """Public read-only serializer for archive videos."""

    youtube_url = YoutubeUrlField(read_only=True)

    class Meta:
        model = OtherVideo
        fields = (
            "id",
            "category",
            "name",
            "description",
            "youtube_url",
        )
