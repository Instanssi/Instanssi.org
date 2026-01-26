from rest_framework.serializers import ModelSerializer, SerializerMethodField

from Instanssi.admin_upload.models import UploadedFile


class UploadedFileSerializer(ModelSerializer[UploadedFile]):
    file_url = SerializerMethodField()
    filename = SerializerMethodField()

    class Meta:
        model = UploadedFile
        fields = (
            "id",
            "event",
            "user",
            "description",
            "file",
            "file_url",
            "filename",
            "date",
        )
        read_only_fields = (
            "id",
            "event",  # Set from URL, not request body
            "file_url",
            "filename",
            "date",
        )

    def get_file_url(self, obj: UploadedFile) -> str | None:
        """Return absolute URL for the file."""
        if not obj.file:
            return None
        if request := self.context.get("request"):
            return str(request.build_absolute_uri(obj.file.url))
        return str(obj.file.url)

    def get_filename(self, obj: UploadedFile) -> str:
        """Return just the filename without path."""
        return obj.name()
