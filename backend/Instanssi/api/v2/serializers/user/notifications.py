from typing import Any, Dict

from django.core.validators import URLValidator
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from Instanssi.notifications.models import PushSubscription


class PushSubscriptionSerializer(ModelSerializer[PushSubscription]):
    class Meta:
        model = PushSubscription
        fields = ("id", "endpoint", "p256dh", "auth", "created_at")
        read_only_fields = ("id", "created_at")
        # Remove unique validator from endpoint — upsert is handled in the viewset
        extra_kwargs: Dict[str, Dict[str, Any]] = {"endpoint": {"validators": []}}

    def validate_endpoint(self, value: str) -> str:
        if not value.startswith("https://"):
            raise serializers.ValidationError("Push endpoint must use HTTPS.")
        URLValidator(schemes=["https"])(value)
        return value
