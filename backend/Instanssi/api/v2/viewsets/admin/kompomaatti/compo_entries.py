from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.serializers import BaseSerializer

from Instanssi.api.v2.serializers.admin.kompomaatti import CompoEntrySerializer
from Instanssi.api.v2.utils.base import PermissionViewSet
from Instanssi.kompomaatti.models import Compo, Entry

from .entry_viewset_mixin import EntryViewSetMixin


class CompoEntryViewSet(EntryViewSetMixin, PermissionViewSet):  # type: ignore[misc]
    """Staff viewset for managing compo entries.

    Staff can manage entries without deadline restrictions.
    Compo-event validation and file deletion are handled by the mixin.
    """

    queryset = Entry.objects.all()
    serializer_class = CompoEntrySerializer  # type: ignore[assignment]
    parser_classes = (MultiPartParser, FormParser)
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    ordering_fields = ("id", "compo", "name", "creator", "user")
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
        serializer.save()

    def perform_update(self, serializer: BaseSerializer[Entry]) -> None:  # type: ignore[override]
        if compo := serializer.validated_data.get("compo"):
            self.validate_compo_belongs_to_event(compo)
        serializer.save()
