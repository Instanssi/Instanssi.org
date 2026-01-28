from typing import Any

from rest_framework.fields import CharField
from rest_framework.serializers import Serializer


class SocialAuthURLSerializer(Serializer[dict[str, Any]]):
    """Serializer for social authentication provider URLs."""

    method = CharField()
    url = CharField()
    name = CharField()
