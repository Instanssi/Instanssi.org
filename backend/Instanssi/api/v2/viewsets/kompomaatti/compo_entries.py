from typing import Any

from django.db.models import QuerySet
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import SAFE_METHODS
from rest_framework.request import Request
from rest_framework.serializers import BaseSerializer
from rest_framework.views import APIView

from Instanssi.api.v2.serializers.kompomaatti import CompoEntrySerializer
from Instanssi.api.v2.utils.base import FullDjangoModelPermissions, PermissionViewSet
from Instanssi.kompomaatti.models import Compo, Entry

from .entry_viewset_mixin import EntryViewSetMixin


class CompoEntryPermissions(FullDjangoModelPermissions):
    """Allow public read access to compo entries after voting has started"""

    def has_permission(self, request: Request, view: APIView) -> bool:
        # Allow public read access (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return True
        # For write operations, require full permissions
        return super().has_permission(request, view)


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
    permission_classes = [CompoEntryPermissions]

    def get_queryset(self) -> QuerySet[Entry]:
        """Filter entries by event from URL.

        For non-staff users, only show entries from active compos where voting has started.
        """
        event_id = int(self.kwargs["event_pk"])
        queryset = (
            self.queryset.filter(compo__event_id=event_id)
            .select_related("compo")
            .prefetch_related("alternate_files")
        )

        # Staff users can see all entries
        if self.request.user.is_authenticated and self.request.user.has_perm("kompomaatti.view_entry"):
            return queryset

        # Public users can only see entries from active compos where voting has started
        return queryset.filter(compo__active=True, compo__voting_start__lte=timezone.now())

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
