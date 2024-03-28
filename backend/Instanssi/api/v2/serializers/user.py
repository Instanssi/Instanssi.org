from django.contrib.auth.models import Permission, User
from rest_framework.serializers import ModelSerializer


class PermissionSerializer(ModelSerializer):
    class Meta:
        model = Permission
        fields = ("name", "codename")


class UserInfoSerializer(ModelSerializer):
    user_permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email", "user_permissions", "is_superuser")
