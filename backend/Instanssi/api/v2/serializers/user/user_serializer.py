from .group_serializer import GroupSerializer
from .user_info_serializer import UserInfoSerializer


class UserSerializer(UserInfoSerializer):
    """Staff serializer for users, extends UserInfoSerializer with groups and active status."""

    groups = GroupSerializer(many=True, read_only=True)

    class Meta(UserInfoSerializer.Meta):
        fields = UserInfoSerializer.Meta.fields + (  # type: ignore[assignment]
            "groups",
            "is_active",
        )
