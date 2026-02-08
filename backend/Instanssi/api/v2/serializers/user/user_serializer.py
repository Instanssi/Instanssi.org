from typing import Any

from django.contrib.auth.models import Group
from rest_framework.serializers import PrimaryKeyRelatedField

from .group_serializer import GroupSerializer
from .user_info_serializer import UserInfoSerializer


class UserSerializer(UserInfoSerializer):
    """Staff serializer for users, extends UserInfoSerializer with groups and active status."""

    groups = GroupSerializer(many=True, read_only=True)
    group_ids = PrimaryKeyRelatedField(
        many=True, queryset=Group.objects.all(), source="groups", write_only=True, required=False
    )

    class Meta(UserInfoSerializer.Meta):
        fields = UserInfoSerializer.Meta.fields + (  # type: ignore[assignment]
            "groups",
            "group_ids",
            "is_active",
            "is_staff",
            "is_system",
        )
        read_only_fields = UserInfoSerializer.Meta.read_only_fields + ("is_staff", "is_system")  # type: ignore[assignment]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user.is_superuser:
            self.fields["is_staff"].read_only = False
