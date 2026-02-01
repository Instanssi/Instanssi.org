from datetime import datetime, timezone
from typing import Any

from knox.models import AuthToken
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer


class AuthTokenSerializer(ModelSerializer[AuthToken]):
    """Read-only serializer for listing tokens."""

    class Meta:
        model = AuthToken
        fields = ("pk", "token_key", "created", "expiry", "user")
        read_only_fields = fields


class AuthTokenCreateSerializer(Serializer[dict[str, Any]]):
    """Input serializer for token creation."""

    expiry = serializers.DateTimeField(required=True)

    def validate_expiry(self, value: datetime) -> datetime:
        if value <= datetime.now(timezone.utc):
            raise serializers.ValidationError("Expiry must be in the future")
        return value


class AuthTokenCreateResponseSerializer(Serializer[dict[str, Any]]):
    """Response with plain token (shown only once)."""

    pk = serializers.CharField()
    token_key = serializers.CharField()
    token = serializers.CharField()  # Full token, shown once
    created = serializers.DateTimeField()
    expiry = serializers.DateTimeField()
