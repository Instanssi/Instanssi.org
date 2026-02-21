from collections.abc import Iterator
from pathlib import Path
from typing import cast

from django.db.models import QuerySet
from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from Instanssi.api.v2.serializers.admin.kompomaatti import CompoEntrySerializer
from Instanssi.api.v2.utils.base import PermissionViewSet
from Instanssi.api.v2.utils.entry_file_validation import (
    maybe_copy_entry_to_image,
    validate_entry_files,
)
from Instanssi.api.v2.utils.zip_stream import generate_zip_stream
from Instanssi.common.file_handling import clean_filename
from Instanssi.kompomaatti.models import Compo, Entry, Event


class CompoEntryViewSet(PermissionViewSet):
    """Staff viewset for managing compo entries.

    Staff can manage entries without deadline restrictions.
    Supports ordering by rank and score.
    """

    queryset = Entry.objects.all()
    serializer_class = CompoEntrySerializer  # type: ignore[assignment]
    parser_classes = (MultiPartParser, FormParser)
    ordering_fields = (
        "id",
        "compo",
        "name",
        "creator",
        "user",
        "disqualified",
        "computed_rank",
        "computed_score",
    )
    search_fields = ("name", "creator", "description")
    filterset_fields = ("compo", "disqualified", "user")

    def get_queryset(self) -> QuerySet[Entry]:
        """Filter entries by event from URL."""
        event_id = int(self.kwargs["event_pk"])
        return (
            self.queryset.filter(compo__event_id=event_id)
            .select_related("compo")
            .prefetch_related("alternate_files")
            .with_rank()
        )

    def validate_compo_belongs_to_event(self, compo: Compo) -> None:
        """Validate that compo belongs to the event in the URL."""
        event_id = int(self.kwargs["event_pk"])
        if compo.event_id != event_id:
            raise serializers.ValidationError({"compo": [_("Compo does not belong to this event")]})

    def _refresh_with_annotations(self, serializer: BaseSerializer[Entry]) -> None:
        """Refresh the serializer instance with score/rank annotations."""
        assert serializer.instance is not None
        serializer.instance = self.get_queryset().get(pk=serializer.instance.pk)

    def perform_create(self, serializer: BaseSerializer[Entry]) -> None:  # type: ignore[override]
        if compo := serializer.validated_data.get("compo"):
            self.validate_compo_belongs_to_event(compo)
            validate_entry_files(serializer.validated_data, compo)
        instance = serializer.save()
        maybe_copy_entry_to_image(instance)
        self._refresh_with_annotations(serializer)

    def perform_update(self, serializer: BaseSerializer[Entry]) -> None:  # type: ignore[override]
        assert serializer.instance is not None
        if new_compo := serializer.validated_data.get("compo"):
            if new_compo.id != serializer.instance.compo_id:
                raise serializers.ValidationError({"compo": [_("Cannot change compo after creation")]})
        validate_entry_files(serializer.validated_data, serializer.instance.compo, serializer.instance)
        instance = serializer.save()
        maybe_copy_entry_to_image(instance)
        self._refresh_with_annotations(serializer)

    def _collect_archive_files(self, event_pk: int) -> tuple[list[tuple[str, Path]], list[str]]:
        """Collect entry files for archiving and check for missing files.

        Returns a tuple of (files, missing_files) where files is a list of
        (archive_name, file_path) tuples and missing_files is a list of
        human-readable descriptions of entries with missing files on disk.
        """
        base_queryset = (
            self.queryset.filter(compo__event_id=event_pk)
            .filter(disqualified=False)
            .exclude(entryfile="")
            .select_related("compo")
            .with_rank()
            .only("id", "name", "entryfile", "compo__name")
        )
        queryset = self.filter_queryset(base_queryset)

        files: list[tuple[str, Path]] = []
        missing_files: list[str] = []

        for entry in cast(Iterator[Entry], queryset.iterator()):
            file_path = Path(entry.entryfile.path)
            if not file_path.is_file():
                missing_files.append(f"[{entry.compo.name}] Entry {entry.id}: {entry.name}")
            else:
                archive_name = (
                    f"{clean_filename(entry.compo.name)}/{entry.computed_rank:03d}__{file_path.name}"
                )
                files.append((archive_name, file_path))

        return files, missing_files

    @extend_schema(
        parameters=[OpenApiParameter("compo", int, description="Filter by compo ID")],
        responses={
            200: inline_serializer(
                "ValidateArchiveOk",
                fields={
                    "ok": serializers.BooleanField(),
                    "count": serializers.IntegerField(),
                },
            ),
            400: inline_serializer(
                "ValidateArchiveError",
                fields={
                    "error": serializers.CharField(),
                    "entries": serializers.ListField(child=serializers.CharField()),
                },
            ),
        },
        summary="Validate entry files archive",
        description=(
            "Checks that all entry files exist on disk before downloading. "
            "Call this before download-archive to get actionable error messages."
        ),
    )
    @action(detail=False, methods=["get"], url_path="validate-archive")
    def validate_archive(self, request: Request, event_pk: int = 0) -> Response:
        """Validate that all entry files are present on disk.

        Returns 200 with entry count on success, or 400 with details about
        missing files. Supports the same query parameters as download-archive.
        """
        get_object_or_404(Event, pk=event_pk)
        files, missing_files = self._collect_archive_files(event_pk)

        if missing_files:
            return Response(
                {"error": "Missing entry files on disk", "entries": missing_files},
                status=400,
            )

        return Response({"ok": True, "count": len(files)})

    @extend_schema(
        parameters=[OpenApiParameter("compo", int, description="Filter by compo ID")],
        responses={(200, "application/zip"): bytes},
        summary="Download entry files archive",
        description="Streams all entry files as a ZIP archive organized by compo directory.",
    )
    @action(detail=False, methods=["get"], url_path="download-archive")
    def download_archive(self, request: Request, event_pk: int = 0) -> StreamingHttpResponse | Response:
        """Download entry files as a .zip archive.

        Streams all entry files organized by compo directory, with rank prefix.
        Disqualified entries are excluded. Supports filtering via query params.

        Query parameters (inherited from viewset):
            compo: Filter by compo ID
            user: Filter by user ID
        """
        event = get_object_or_404(Event, pk=event_pk)
        files, missing_files = self._collect_archive_files(event_pk)

        if missing_files:
            return Response(
                {"error": "Missing entry files on disk", "entries": missing_files},
                status=400,
            )

        response = StreamingHttpResponse(
            generate_zip_stream(files),
            content_type="application/zip",
        )
        name_parts = [f"entries_{event.tag or event.id}"]
        if compo_id := request.query_params.get("compo"):
            compo = Compo.objects.filter(pk=compo_id, event_id=event_pk).first()
            if compo:
                name_parts.append(clean_filename(compo.name))
        archive_filename = f"{'_'.join(name_parts)}.zip"
        response["Content-Disposition"] = f'attachment; filename="{archive_filename}"'
        return response
