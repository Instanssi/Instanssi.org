from typing import Any

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.serializers import BaseSerializer

from Instanssi.api.v2.serializers.admin.kompomaatti import CompoSerializer
from Instanssi.api.v2.utils.base import PermissionViewSet
from Instanssi.kompomaatti.models import Compo, Entry

IMAGE_FORMATS = {"png", "jpg", "jpeg"}


class CompoViewSet(PermissionViewSet):
    """Staff viewset for managing compos."""

    queryset = Compo.objects.all()
    serializer_class = CompoSerializer  # type: ignore[assignment]
    ordering_fields = (
        "id",
        "event",
        "name",
        "adding_end",
        "compo_start",
        "voting_start",
        "voting_end",
        "active",
    )
    search_fields = ("name", "description")
    filterset_fields = (
        "active",
        "show_voting_results",
        "is_votable",
        "hide_from_archive",
        "hide_from_frontpage",
    )

    def get_queryset(self) -> QuerySet[Compo]:
        """Filter compos by event from URL."""
        event_id = int(self.kwargs["event_pk"])
        return self.queryset.filter(event_id=event_id)

    @staticmethod
    def _validate_thumbnail_pref(data: dict[str, Any]) -> None:
        """Validate that automatic thumbnails are only used with image-only formats."""
        thumbnail_pref = data.get("thumbnail_pref")
        formats = data.get("formats")
        if thumbnail_pref == 1 and formats is not None:
            format_list = [f.strip().lower() for f in formats.split("|") if f.strip()]
            if not all(f in IMAGE_FORMATS for f in format_list):
                raise serializers.ValidationError(
                    {
                        "thumbnail_pref": [
                            _("Automatic thumbnails require image-only entry formats (png, jpg)")
                        ]
                    }
                )

    def perform_create(self, serializer: BaseSerializer[Compo]) -> None:  # type: ignore[override]
        """Set event from URL when creating."""
        self._validate_thumbnail_pref(serializer.validated_data)
        serializer.save(event_id=int(self.kwargs["event_pk"]))

    def perform_update(self, serializer: BaseSerializer[Compo]) -> None:  # type: ignore[override]
        """Validate thumbnail settings on update."""
        assert serializer.instance is not None
        merged = {
            "thumbnail_pref": serializer.instance.thumbnail_pref,
            "formats": serializer.instance.formats,
        }
        merged.update(serializer.validated_data)
        self._validate_thumbnail_pref(merged)
        serializer.save()

    def perform_destroy(self, instance: Compo) -> None:  # type: ignore[override]
        """Prevent deletion of compos that have entries."""
        if Entry.objects.filter(compo=instance).exists():
            raise serializers.ValidationError({"detail": _("Cannot delete a compo that has entries")})
        super().perform_destroy(instance)
