from django.contrib.auth.models import Group, Permission, User
from rest_framework.serializers import ModelSerializer


class PermissionSerializer(ModelSerializer):
    class Meta:
        model = Permission
        fields = ("name", "codename")


class GroupSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = ("name",)


class UserInfoSerializer(ModelSerializer):
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


class UserSerializer(UserInfoSerializer):
    groups = GroupSerializer(many=True, read_only=True)

    class Meta(UserInfoSerializer.Meta):
        fields = UserInfoSerializer.Meta.fields + (
            "groups",
            "is_active",
        )
