from typing import Any

from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from Instanssi.users.models import User


class ContentTypeSerializer(serializers.ModelSerializer[ContentType]):
    """Serializer for content type information."""

    class Meta:
        model = ContentType
        fields = ("id", "app_label", "model")


class ActorSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """Serializer for the actor (user) who made the change."""

    class Meta:
        model = User
        fields = ("id", "username")


class LogEntrySerializer(serializers.ModelSerializer[LogEntry]):
    """Serializer for audit log entries."""

    content_type = ContentTypeSerializer(read_only=True)
    actor = ActorSerializer(read_only=True)
    changes = serializers.SerializerMethodField()

    class Meta:
        model = LogEntry
        fields = (
            "id",
            "content_type",
            "object_pk",
            "object_repr",
            "action",
            "changes",
            "timestamp",
            "actor",
            "remote_addr",
        )

    def get_changes(self, obj: LogEntry) -> dict[str, Any]:
        """Return the changes as a dictionary."""
        return obj.changes_dict or {}
