from drf_spectacular.utils import extend_schema_field
from rest_framework.serializers import (
    CharField,
    ListField,
    ModelSerializer,
    SerializerMethodField,
)

from Instanssi.users.models import User


class UserInfoSerializer(ModelSerializer[User]):
    """Serializer for the authenticated user's own profile and permissions."""

    user_permissions = SerializerMethodField()

    @extend_schema_field(ListField(child=CharField()))
    def get_user_permissions(self, user: User) -> list[str]:
        if user.is_superuser:
            return []
        return [perm.split(".")[1] for perm in user.get_all_permissions()]

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
            "language",
        )
        read_only_fields = ("date_joined", "is_superuser")
