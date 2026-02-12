from django.contrib.auth.models import Group
from rest_framework.serializers import ModelSerializer


class GroupSerializer(ModelSerializer[Group]):
    """Serializer for user groups (used in user info responses)."""

    class Meta:
        model = Group
        fields = ("id", "name")
