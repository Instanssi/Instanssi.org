from typing import Dict, Final, List, Tuple

from django.db.models import IntegerChoices


class MediaCodec(IntegerChoices):
    AAC = 0
    OPUS = 1


class MediaContainer(IntegerChoices):
    MP4 = 0
    WEBM = 1


WEB_AUDIO_FORMATS: Final[List[Tuple[MediaCodec, MediaContainer]]] = [
    (MediaCodec.OPUS, MediaContainer.WEBM),
    (MediaCodec.AAC, MediaContainer.MP4),
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

# Extensions that browsers can generally play natively in <audio> elements.
BROWSER_AUDIO_EXTENSIONS: Final[Dict[str, str]] = {
    ".mp3": "audio/mpeg",
    ".ogg": "audio/ogg",
    ".oga": "audio/ogg",
    ".opus": "audio/ogg;codecs=opus",
    ".m4a": "audio/mp4",
    ".mp4": "audio/mp4",
    ".aac": "audio/aac",
}
