from typing import TYPE_CHECKING, Any

from rest_framework.request import Request
from rest_framework.response import Response

from Instanssi.kompomaatti.models import Entry

if TYPE_CHECKING:
    from rest_framework.serializers import Serializer


class EntryViewSetMixin:
    """Mixin providing common functionality for Entry viewsets.

    Provides:
    - File deletion handling in partial_update
    """

    # Type hints for mixin - these come from the viewset
    # Note: request is accessed via self but not declared to avoid conflict with View.request
    kwargs: dict[str, Any]

    # These methods are provided by the viewset - declared here for type checking only
    if TYPE_CHECKING:

        def get_object(self) -> Entry: ...

        def get_serializer(
            self, instance: Entry | None = None, data: Any = None, **kwargs: Any
        ) -> Serializer[Entry]: ...

        def perform_update(self, serializer: Serializer[Entry]) -> None: ...

    def partial_update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Handle partial updates with file deletion support.

        Files can be deleted by sending an empty string for the field.
        Subclasses can override validate_partial_update() to add extra checks.
        """
        instance = self.get_object()

        # Allow subclasses to add validation (e.g., deadline checks)
        self.validate_partial_update(instance)

        delete_image_file = False
        delete_source_file = False

        # Remove image file if requested (field is empty string)
        if (
            instance.imagefile_original is not None
            and "imagefile_original" in request.data
            and len(request.data["imagefile_original"]) == 0
        ):
            delete_image_file = True

        # Remove sourcefile if requested (field is empty string)
        if (
            instance.sourcefile is not None
            and "sourcefile" in request.data
            and len(request.data["sourcefile"]) == 0
        ):
            delete_source_file = True

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        if delete_image_file:
            instance.imagefile_original = None
        if delete_source_file:
            instance.sourcefile = None

        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}  # type: ignore[attr-defined]

        return Response(serializer.data)

    def validate_partial_update(self, instance: Entry) -> None:
        """Hook for subclasses to add validation before partial update.

        Override this to add checks like deadline validation.
        """
        pass
