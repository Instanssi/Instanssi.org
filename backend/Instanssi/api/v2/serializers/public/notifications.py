from typing import Any

from rest_framework import serializers


class VapidPublicKeySerializer(serializers.Serializer[Any]):
    vapid_public_key = serializers.CharField(read_only=True)
