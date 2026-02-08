from typing import Any

from .group_serializer import GroupSerializer
from .user_info_serializer import UserInfoSerializer


class UserSerializer(UserInfoSerializer):
    """Staff serializer for users, extends UserInfoSerializer with groups and active status."""

    groups = GroupSerializer(many=True, read_only=True)

    class Meta(UserInfoSerializer.Meta):
        fields = UserInfoSerializer.Meta.fields + (  # type: ignore[assignment]
            "groups",
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
