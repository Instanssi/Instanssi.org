from django.conf import settings
from django.db import models
from django.utils import timezone


class PushSubscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="push_subscriptions",
    )
    endpoint = models.CharField(max_length=1024, unique=True)
    p256dh = models.CharField(max_length=128)
    auth = models.CharField(max_length=64)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return f"PushSubscription({self.user}, {self.endpoint[:50]})"


class SentNotification(models.Model):
    notification_key = models.CharField(max_length=255, unique=True)
    sent_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return f"SentNotification({self.notification_key})"
