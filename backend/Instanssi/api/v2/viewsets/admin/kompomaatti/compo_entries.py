from django.db.models import QuerySet
from rest_framework import serializers
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.serializers import BaseSerializer

from Instanssi.api.v2.serializers.admin.kompomaatti import CompoEntrySerializer
from Instanssi.api.v2.utils.base import PermissionViewSet
from Instanssi.api.v2.utils.entry_file_validation import (
    maybe_copy_entry_to_image,
    validate_entry_files,
)
from Instanssi.kompomaatti.models import Compo, Entry


class CompoEntryViewSet(PermissionViewSet):
    """Staff viewset for managing compo entries.

    Staff can manage entries without deadline restrictions.
    """

    queryset = Entry.objects.all()
    serializer_class = CompoEntrySerializer  # type: ignore[assignment]
    parser_classes = (MultiPartParser, FormParser)
    ordering_fields = ("id", "compo", "name", "creator", "user", "disqualified")
    search_fields = ("name", "creator", "description")
    filterset_fields = ("compo", "disqualified", "user")

    def get_queryset(self) -> QuerySet[Entry]:
        """Filter entries by event from URL."""
        event_id = int(self.kwargs["event_pk"])
        return (
            self.queryset.filter(compo__event_id=event_id)
            .select_related("compo")
            .prefetch_related("alternate_files")
        )

    def validate_compo_belongs_to_event(self, compo: Compo) -> None:
        """Validate that compo belongs to the event in the URL."""
        event_id = int(self.kwargs["event_pk"])
        if compo.event_id != event_id:
            raise serializers.ValidationError({"compo": ["Compo does not belong to this event"]})

    def perform_create(self, serializer: BaseSerializer[Entry]) -> None:  # type: ignore[override]
        if compo := serializer.validated_data.get("compo"):
            self.validate_compo_belongs_to_event(compo)
            validate_entry_files(serializer.validated_data, compo)
        instance = serializer.save()
        maybe_copy_entry_to_image(instance)

    def perform_update(self, serializer: BaseSerializer[Entry]) -> None:  # type: ignore[override]
        assert serializer.instance is not None
        if new_compo := serializer.validated_data.get("compo"):
            if new_compo.id != serializer.instance.compo_id:
                raise serializers.ValidationError({"compo": ["Cannot change compo after creation"]})
        validate_entry_files(serializer.validated_data, serializer.instance.compo, serializer.instance)
        instance = serializer.save()
        maybe_copy_entry_to_image(instance)
