from django.contrib.auth.models import Permission
from rest_framework.serializers import ModelSerializer


class PermissionSerializer(ModelSerializer[Permission]):
    """Serializer for user permissions (used in user info responses)."""

    class Meta:
        model = Permission
        fields = ("name", "codename")
