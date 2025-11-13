from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import SAFE_METHODS

from Instanssi.api.v2.serializers.kompomaatti import CompoEntrySerializer
from Instanssi.api.v2.utils.base import FullDjangoModelPermissions, PermissionViewSet
from Instanssi.kompomaatti.models import Entry


class CompoEntryPermissions(FullDjangoModelPermissions):
    """Allow public read access to compo entries after voting has started"""

    def has_permission(self, request, view):
        # Allow public read access (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return True
        # For write operations, require full permissions
        return super().has_permission(request, view)


class CompoEntryViewSet(PermissionViewSet):
    queryset = Entry.objects.all()
    serializer_class = CompoEntrySerializer
    parser_classes = (MultiPartParser, FormParser)
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    ordering_fields = ("id", "compo", "name", "creator", "user")
    filterset_fields = ("compo", "disqualified", "user")
    permission_classes = [CompoEntryPermissions]

    def get_queryset(self):
        """Filter entries by event from URL.

        For non-staff users, only show entries from active compos where voting has started.
        """
        event_id = self.kwargs.get("event_pk")
        queryset = self.queryset.filter(compo__event_id=event_id)

        # Staff users can see all entries
        if self.request.user.is_authenticated and self.request.user.has_perm("kompomaatti.view_entry"):
            return queryset

        # Public users can only see entries from active compos where voting has started
        return queryset.filter(compo__active=True, compo__voting_start__lte=timezone.now())
