from django.contrib.auth.models import Permission
from rest_framework.serializers import ModelSerializer


class PermissionSerializer(ModelSerializer[Permission]):
    class Meta:
        model = Permission
        fields = ("name", "codename")
