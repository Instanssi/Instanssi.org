from typing import Any

from rest_framework import serializers


class ArchiverStatusSerializer(serializers.Serializer[Any]):
    """Serializer for archiver status response."""

    is_archived = serializers.BooleanField(help_text="Whether the event is visible in the public archive")
    has_non_archived_items = serializers.BooleanField(
        help_text="Whether there are entries/participations not owned by archive user"
    )
    ongoing_activity = serializers.BooleanField(help_text="Whether the event is still ongoing")
    votes_unoptimized = serializers.BooleanField(
        help_text="Whether voting results need to be pre-calculated (archive_score/archive_rank not set)"
    )
    old_votes_found = serializers.BooleanField(help_text="Whether there are old vote records to clean up")
