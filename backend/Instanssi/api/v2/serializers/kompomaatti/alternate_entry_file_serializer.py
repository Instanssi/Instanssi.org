from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from Instanssi.kompomaatti.models import AlternateEntryFile


class AlternateEntryFileSerializer(ModelSerializer):
    url = SerializerMethodField()
    format = SerializerMethodField()

    def get_url(self, obj: AlternateEntryFile) -> str:
        return self.context["request"].build_absolute_uri(obj.file.url)

    def get_format(self, obj: AlternateEntryFile) -> str:
        return obj.mime_format

    class Meta:
        model = AlternateEntryFile
        fields = (
            "format",
            "url",
        )
