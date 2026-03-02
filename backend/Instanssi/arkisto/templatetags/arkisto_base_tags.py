from pathlib import PurePosixPath
from typing import Any

from django import template
from django.db.models.fields.files import FieldFile

from Instanssi.kompomaatti.models import Event

register = template.Library()

# Mirrors admin/src/utils/media.ts extension lists
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".webm", ".avi", ".mov", ".wmv", ".flv", ".ogv"}
AUDIO_EXTENSIONS = {".mp3", ".ogg", ".opus", ".aac", ".wav", ".flac", ".m4a", ".wma"}


@register.inclusion_tag("arkisto/arkisto_nav_items.html")
def render_arkisto_nav(current_event_id: int | str = 0) -> dict[str, Any]:
    return {
        "events": Event.objects.filter(archived=True).order_by("-date"),
        "current_event_id": current_event_id,
    }


@register.filter
def media_type(value: str | FieldFile | None) -> str:
    """Detect media type from a filename or FieldFile. Returns 'video', 'audio', or 'other'."""
    if value is None:
        return "other"
    name = value.name if isinstance(value, FieldFile) else str(value)
    if not name:
        return "other"
    ext = PurePosixPath(name).suffix.lower()
    if ext in VIDEO_EXTENSIONS:
        return "video"
    if ext in AUDIO_EXTENSIONS:
        return "audio"
    return "other"


@register.filter
def dotfill(value: str, width: int) -> str:
    """Pad a string with dots to fill the given width. e.g. 'Hello' | dotfill:40 => 'Hello ...................................'"""
    value = str(value)
    if len(value) >= width - 2:
        return value
    dots = "." * (width - len(value) - 1)
    return f"{value} {dots}"
