from typing import Any, cast

from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response

from Instanssi.api.v2.serializers.admin import UserSerializer
from Instanssi.api.v2.utils.base import PermissionViewSet
from Instanssi.users.models import User

SYSTEM_USER_ERROR = _("System users cannot be modified.")


class UserViewSet(PermissionViewSet):
    """Staff viewset for managing users."""

    queryset = User.objects.all()
    serializer_class = UserSerializer  # type: ignore[assignment]
    ordering_fields = (
        "id",
        "username",
        "first_name",
        "last_name",
        "email",
        "date_joined",
        "is_active",
        "is_staff",
        "is_system",
    )
    filterset_fields = ("email", "username", "is_active", "is_superuser", "is_staff", "is_system")
    search_fields = ("username", "first_name", "last_name", "email")

    def _check_not_system_user(self) -> None:
        if cast(User, self.get_object()).is_system:
            raise PermissionDenied(SYSTEM_USER_ERROR)

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        self._check_not_system_user()
        return super().update(request, *args, **kwargs)

    def partial_update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        self._check_not_system_user()
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        self._check_not_system_user()
        return super().destroy(request, *args, **kwargs)
