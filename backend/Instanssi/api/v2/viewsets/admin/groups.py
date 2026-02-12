from django.contrib.auth.models import Group

from Instanssi.api.v2.serializers.admin import GroupSerializer
from Instanssi.api.v2.utils.base import PermissionReadOnlyViewSet


class GroupViewSet(PermissionReadOnlyViewSet):
    """Read-only viewset for listing groups."""

    queryset = Group.objects.all()
    serializer_class = GroupSerializer  # type: ignore[assignment]
    ordering_fields = ("id", "name")
    search_fields = ("name",)
