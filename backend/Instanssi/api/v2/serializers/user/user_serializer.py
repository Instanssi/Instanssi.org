from .group_serializer import GroupSerializer
from .user_info_serializer import UserInfoSerializer


class UserSerializer(UserInfoSerializer):
    groups = GroupSerializer(many=True, read_only=True)

    class Meta(UserInfoSerializer.Meta):
        fields = UserInfoSerializer.Meta.fields + (  # type: ignore[assignment]
            "groups",
            "is_active",
        )
