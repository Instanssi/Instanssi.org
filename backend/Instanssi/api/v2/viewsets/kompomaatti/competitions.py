from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import SAFE_METHODS

from Instanssi.api.v2.serializers.kompomaatti import CompetitionSerializer
from Instanssi.api.v2.utils.base import FullDjangoModelPermissions, PermissionViewSet
from Instanssi.kompomaatti.models import Competition


class ActiveCompetitionReadPermission(FullDjangoModelPermissions):
    """Allow read access to active competitions for everyone, full permissions for staff"""

    def has_permission(self, request, view):
        # Allow read access for safe methods (GET, HEAD, OPTIONS) without authentication
        if request.method in SAFE_METHODS:
            return True
        # For write operations, check Django model permissions
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        # Allow read access to active competitions for everyone
        if request.method in SAFE_METHODS and obj.active:
            return True
        # For write operations or inactive competitions, check Django model permissions
        return super().has_permission(request, view)


class CompetitionViewSet(PermissionViewSet):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    ordering_fields = ("id", "event", "name", "start")
    filterset_fields = ("active", "show_results", "hide_from_archive")
    permission_classes = [ActiveCompetitionReadPermission]

    def get_queryset(self):
        """Filter competitions by event from URL"""
        event_id = self.kwargs.get("event_pk")
        queryset = self.queryset.filter(event_id=event_id)

        # For non-staff users, only show active competitions
        if not self.request.user.is_authenticated or not self.request.user.has_perm(
            "kompomaatti.view_competition"
        ):
            queryset = queryset.filter(active=True)

        return queryset
