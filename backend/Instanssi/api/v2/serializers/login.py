from rest_framework.fields import CharField
from rest_framework.serializers import Serializer


class UserLoginSerializer(Serializer):
    username = CharField(min_length=0, max_length=255)
    password = CharField(min_length=0, max_length=255)
