from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer


class UserDataSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email", "user_permissions", "is_superuser")
