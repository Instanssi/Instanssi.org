from typing import Any, Dict

from rest_framework.serializers import ModelSerializer

from Instanssi.notifications.models import PushSubscription


class PushSubscriptionSerializer(ModelSerializer[PushSubscription]):
    class Meta:
        model = PushSubscription
        fields = ("id", "endpoint", "p256dh", "auth", "created_at")
        read_only_fields = ("id", "created_at")
        # Remove unique validator from endpoint — upsert is handled in the viewset
        extra_kwargs: Dict[str, Dict[str, Any]] = {"endpoint": {"validators": []}}
