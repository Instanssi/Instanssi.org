from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import SAFE_METHODS
from rest_framework.request import Request
from rest_framework.serializers import BaseSerializer
from rest_framework.views import APIView

from Instanssi.api.v2.serializers.kompomaatti import CompetitionSerializer
from Instanssi.api.v2.utils.base import FullDjangoModelPermissions, PermissionViewSet
from Instanssi.kompomaatti.models import Competition


class ActiveCompetitionReadPermission(FullDjangoModelPermissions):
    """Allow read access to active competitions for everyone, full permissions for staff."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return super().has_permission(request, view)

    def has_object_permission(self, request: Request, view: APIView, obj: Competition) -> bool:
        if request.method in SAFE_METHODS and obj.active:
            return True
        return super().has_permission(request, view)


class CompetitionViewSet(PermissionViewSet):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer  # type: ignore[assignment]
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    ordering_fields = ("id", "event", "name", "start")
    search_fields = ("name", "description")
    filterset_fields = ("active", "show_results", "hide_from_archive")
    permission_classes = [ActiveCompetitionReadPermission]

    def get_queryset(self) -> QuerySet[Competition]:
        """Filter competitions by event from URL"""
        event_id = int(self.kwargs["event_pk"])
        queryset = self.queryset.filter(event_id=event_id)

        # For non-staff users, only show active competitions
        if not self.request.user.is_authenticated or not self.request.user.has_perm(
            "kompomaatti.view_competition"
        ):
            queryset = queryset.filter(active=True)

        return queryset

    def perform_create(self, serializer: BaseSerializer[Competition]) -> None:  # type: ignore[override]
        """Set event from URL when creating."""
        serializer.save(event_id=int(self.kwargs["event_pk"]))
