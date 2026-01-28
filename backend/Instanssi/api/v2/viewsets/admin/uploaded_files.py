from django.db.models import QuerySet
from rest_framework.serializers import BaseSerializer

from Instanssi.admin_upload.models import UploadedFile
from Instanssi.api.v2.serializers.admin import UploadedFileSerializer
from Instanssi.api.v2.utils.base import PermissionViewSet


class UploadedFileViewSet(PermissionViewSet):
    """Uploaded files for an event.

    Staff with admin_upload permissions can manage uploaded files.
    """

    queryset = UploadedFile.objects.all()
    serializer_class = UploadedFileSerializer  # type: ignore[assignment]
    ordering_fields = ("id", "date", "user", "description")
    search_fields = ("description", "file")
    filterset_fields = ("user",)

    def get_queryset(self) -> QuerySet[UploadedFile]:
        """Filter uploaded files by event from URL."""
        event_id = int(self.kwargs["event_pk"])
        return self.queryset.filter(event_id=event_id).order_by("-date")

    def perform_create(self, serializer: BaseSerializer[UploadedFile]) -> None:  # type: ignore[override]
        """Set event from URL when creating."""
        serializer.save(event_id=int(self.kwargs["event_pk"]))
