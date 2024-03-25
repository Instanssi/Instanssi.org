from rest_framework.fields import CharField
from rest_framework.serializers import Serializer


class SocialAuthURLSerializer(Serializer):
    method = CharField()
    url = CharField()
    name = CharField()
