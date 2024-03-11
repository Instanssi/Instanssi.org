from django.contrib.auth.models import User
from rest_framework.fields import CharField
from rest_framework.serializers import ModelSerializer, Serializer


class UserLoginSerializer(Serializer):
    username = CharField(min_length=0, max_length=255)
    password = CharField(min_length=0, max_length=255)


class UserDataSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email", "user_permissions", "is_superuser")
