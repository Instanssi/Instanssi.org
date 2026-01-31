from typing import Any

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from Instanssi.common.youtube import InvalidVideoIdError, YoutubeURL
from Instanssi.common.youtube.parser import InvalidYoutubeUrlError


@extend_schema_field({"type": "string", "nullable": True})
class YoutubeUrlField(serializers.Field):  # type: ignore[type-arg]
    """Custom field to handle YoutubeVideoField serialization/deserialization.

    Accepts and returns YouTube URLs as strings. Internally converts to/from YoutubeURL objects.
    """

    def to_representation(self, value: Any) -> str | None:
        """Convert YoutubeURL object to URL string."""
        if not value:
            return None
        if isinstance(value, YoutubeURL):
            return str(value)
        return None

    def to_internal_value(self, data: Any) -> YoutubeURL | None:
        """Convert URL string to YoutubeURL object."""
        if not data:
            return None
        if isinstance(data, YoutubeURL):
            return data
        try:
            return YoutubeURL.from_url(str(data))
        except (InvalidYoutubeUrlError, InvalidVideoIdError) as e:
            raise serializers.ValidationError(str(e))
