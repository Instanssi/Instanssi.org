from django.contrib.auth import get_user_model

from Instanssi.api.v2.serializers.user import UserSerializer
from Instanssi.api.v2.utils.base import PermissionViewSet


class UserViewSet(PermissionViewSet):
    """Staff viewset for managing users."""

    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer  # type: ignore[assignment]
    ordering_fields = ("id", "username", "first_name", "last_name", "email", "date_joined")
    filterset_fields = ("email", "username", "is_active", "is_superuser", "is_staff")
    search_fields = ("username", "first_name", "last_name", "email")
