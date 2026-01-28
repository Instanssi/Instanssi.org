from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from Instanssi.kompomaatti.models import AlternateEntryFile


class PublicAlternateEntryFileSerializer(ModelSerializer[AlternateEntryFile]):
    url = SerializerMethodField()
    format = SerializerMethodField()

    def get_url(self, obj: AlternateEntryFile) -> str:
        return str(self.context["request"].build_absolute_uri(obj.file.url))

    def get_format(self, obj: AlternateEntryFile) -> str:
        return str(obj.mime_format)

    class Meta:
        model = AlternateEntryFile
        fields = (
            "format",
            "url",
        )
