from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import SAFE_METHODS

from Instanssi.api.v2.serializers.kompomaatti import CompoSerializer
from Instanssi.api.v2.utils.base import FullDjangoModelPermissions, PermissionViewSet
from Instanssi.kompomaatti.models import Compo


class ActiveCompoReadPermission(FullDjangoModelPermissions):
    """Allow read access to active compos for everyone, full permissions for staff"""

    def has_permission(self, request, view):
        # Allow read access for safe methods (GET, HEAD, OPTIONS) without authentication
        if request.method in SAFE_METHODS:
            return True
        # For write operations, check Django model permissions
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        # Allow read access to active compos for everyone
        if request.method in SAFE_METHODS and obj.active:
            return True
        # For write operations or inactive compos, check Django model permissions
        return super().has_permission(request, view)


class CompoViewSet(PermissionViewSet):
    queryset = Compo.objects.all()
    serializer_class = CompoSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    ordering_fields = ("id", "event", "name", "compo_start", "voting_start")
    filterset_fields = (
        "active",
        "show_voting_results",
        "is_votable",
        "hide_from_archive",
        "hide_from_frontpage",
    )
    permission_classes = [ActiveCompoReadPermission]

    def get_queryset(self):
        """Filter compos by event from URL"""
        event_id = self.kwargs.get("event_pk")
        queryset = self.queryset.filter(event_id=event_id)

        # For non-staff users, only show active compos
        if not self.request.user.is_authenticated or not self.request.user.has_perm(
            "kompomaatti.view_compo"
        ):
            queryset = queryset.filter(active=True)

        return queryset
