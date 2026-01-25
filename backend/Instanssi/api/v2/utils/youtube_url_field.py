from typing import Any

from rest_framework import serializers

from Instanssi.common.youtube import YoutubeURL


class YoutubeUrlField(serializers.Field):  # type: ignore[type-arg]
    """Custom field to handle YoutubeVideoField serialization/deserialization."""

    def to_representation(self, value: Any) -> dict[str, Any] | None:
        """Convert YoutubeURL object to dictionary."""
        if not value:
            return None
        if isinstance(value, YoutubeURL):
            return {
                "video_id": value.video_id,
                "start": value.start,
            }
        if isinstance(value, str):
            parsed = YoutubeURL.from_url(value)
            if parsed:
                return {
                    "video_id": parsed.video_id,
                    "start": parsed.start,
                }
        return None

    def to_internal_value(self, data: Any) -> str | None:
        """Accept a URL string and let the model handle parsing."""
        if not data:
            return None
        return str(data)
