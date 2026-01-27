from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import SAFE_METHODS
from rest_framework.request import Request
from rest_framework.serializers import BaseSerializer
from rest_framework.views import APIView

from Instanssi.api.v2.serializers.programme import ProgrammeEventSerializer
from Instanssi.api.v2.utils.base import FullDjangoModelPermissions, PermissionViewSet
from Instanssi.ext_programme.models import ProgrammeEvent


class ActiveProgrammeEventReadPermission(FullDjangoModelPermissions):
    """Allow read access to active programme events for everyone, full permissions for staff."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return super().has_permission(request, view)

    def has_object_permission(self, request: Request, view: APIView, obj: ProgrammeEvent) -> bool:
        if request.method in SAFE_METHODS and obj.active:
            return True
        return super().has_permission(request, view)


class ProgrammeEventViewSet(PermissionViewSet):
    """
    Programme events for an event.

    Public users can read active programme events.
    Staff with ext_programme permissions can manage all programme events.
    """

    queryset = ProgrammeEvent.objects.all()
    serializer_class = ProgrammeEventSerializer  # type: ignore[assignment]
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    ordering_fields = ("id", "start", "end", "title", "event_type")
    search_fields = ("title", "description", "presenters", "place")
    filterset_fields = ("active", "event_type")
    permission_classes = [ActiveProgrammeEventReadPermission]

    def get_queryset(self) -> QuerySet[ProgrammeEvent]:
        """Filter programme events by event from URL."""
        event_id = int(self.kwargs["event_pk"])
        queryset = self.queryset.filter(event_id=event_id)

        # For non-staff users, only show active programme events
        if not self.request.user.is_authenticated or not self.request.user.has_perm(
            "ext_programme.view_programmeevent"
        ):
            queryset = queryset.filter(active=True)

        return queryset.order_by("start")

    def perform_create(self, serializer: BaseSerializer[ProgrammeEvent]) -> None:  # type: ignore[override]
        """Set event from URL when creating."""
        serializer.save(event_id=int(self.kwargs["event_pk"]))
