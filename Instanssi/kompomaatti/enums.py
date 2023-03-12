from typing import Final, List, Tuple

from django.db.models import IntegerChoices


class MediaCodec(IntegerChoices):
    AAC = 0
    OPUS = 1


class MediaContainer(IntegerChoices):
    MP4 = 0
    WEBM = 1


WEB_AUDIO_FORMATS: Final[List[Tuple[MediaCodec, MediaContainer]]] = [
    (MediaCodec.AAC, MediaContainer.MP4),
    (MediaCodec.OPUS, MediaContainer.WEBM),
]

AUDIO_FILE_EXTENSIONS: Final[List[str]] = [
    ".mp3",
    ".ogg",
    ".oga",
    ".webm",
    ".mka",
    ".mp4",
    ".m4a",
    ".opus",
    ".flac",
    ".aac",
    ".wma",
]
