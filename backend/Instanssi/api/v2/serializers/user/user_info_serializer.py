from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer

from .permission_serializer import PermissionSerializer


class UserInfoSerializer(ModelSerializer[User]):
    """Serializer for the authenticated user's own profile and permissions."""

    user_permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "user_permissions",
            "is_superuser",
            "date_joined",
        )
        read_only_fields = ("date_joined", "is_superuser", "user_permissions")
