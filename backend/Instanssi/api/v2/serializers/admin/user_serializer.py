from typing import Any

from django.contrib.auth.models import Group
from drf_spectacular.utils import extend_schema_field
from rest_framework.serializers import (
    CharField,
    ListField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    SerializerMethodField,
)

from Instanssi.api.v2.serializers.admin.group_serializer import GroupSerializer
from Instanssi.users.models import User


class UserSerializer(ModelSerializer[User]):
    """Staff serializer for users, includes all fields for admin management."""

    user_permissions = SerializerMethodField()
    groups = GroupSerializer(many=True, read_only=True)
    group_ids = PrimaryKeyRelatedField(
        many=True, queryset=Group.objects.all(), source="groups", write_only=True, required=False
    )

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
            "groups",
            "group_ids",
            "is_active",
            "is_staff",
            "is_system",
        )
        read_only_fields = ("id", "user_permissions", "date_joined", "is_superuser", "is_staff", "is_system")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user.is_superuser:
            self.fields["is_staff"].read_only = False
