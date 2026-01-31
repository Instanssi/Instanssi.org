import re
from typing import Optional

from yarl import URL

# YouTube video IDs are 11 characters using Base64 URL-safe alphabet
VIDEO_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")


class InvalidYoutubeUrlError(Exception):
    pass


class InvalidVideoIdError(ValueError):
    pass


class InvalidStartTimeError(ValueError):
    pass


class YoutubeURL:
    def __init__(self, video_id: str, start: Optional[int] = None) -> None:
        if not isinstance(video_id, str):
            raise InvalidVideoIdError("video_id must be a string")
        if not VIDEO_ID_PATTERN.match(video_id):
            raise InvalidVideoIdError(
                "video_id must be exactly 11 characters using only A-Z, a-z, 0-9, - and _"
            )
        if start is not None and not isinstance(start, int):
            raise InvalidStartTimeError("start must be an integer or null")
        self.video_id: str = video_id
        self.start: Optional[int] = start

    def __str__(self) -> str:
        """Return a YouTube URL that can be parsed back by from_url()."""
        return self.link_url

    def __repr__(self) -> str:
        return f"YoutubeURL(video_id={self.video_id!r}, start={self.start!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, YoutubeURL):
            return NotImplemented
        return self.video_id == other.video_id and self.start == other.start

    @staticmethod
    def _parse_url(value: str) -> URL:
        if value.startswith(("http://", "https://", "//")):
            return URL(value)
        return URL(f"https://{value}")

    @staticmethod
    def _find_video_id(url: URL) -> Optional[str]:
        if len(url.parts) < 2:  # Path components must be set!
            return None
        if url.host == "youtu.be":  # Shortened url
            return url.parts[1]
        if url.host in ("www.youtube.com", "youtube.com"):
            if url.parts[1] == "watch":
                if "v" in url.query:
                    return url.query["v"]
                return None
            if len(url.parts) == 3:
                if url.parts[1] == "embed":
                    return url.parts[2]
                if url.parts[1] == "v":
                    return url.parts[2]
        return None

    @staticmethod
    def _parse_time_string(time_str: str) -> Optional[int]:
        """Parse YouTube time format strings like '30', '30s', '1m30s', '1h2m30s'."""
        if not time_str:
            return None

        # Try plain integer first
        try:
            return int(time_str)
        except ValueError:
            pass

        # Parse format like "1h2m30s" or "1m30s" or "30s"
        total_seconds = 0
        current_num = ""

        for char in time_str:
            if char.isdigit():
                current_num += char
            elif char == "h" and current_num:
                total_seconds += int(current_num) * 3600
                current_num = ""
            elif char == "m" and current_num:
                total_seconds += int(current_num) * 60
                current_num = ""
            elif char == "s" and current_num:
                total_seconds += int(current_num)
                current_num = ""
            else:
                return None  # Invalid character

        # Handle trailing number without suffix (treat as seconds)
        if current_num:
            total_seconds += int(current_num)

        return total_seconds if total_seconds > 0 else None

    @staticmethod
    def _find_video_start(url: URL) -> Optional[int]:
        start_str: Optional[str] = None
        if "t" in url.query:
            start_str = url.query["t"]
        elif "start" in url.query:
            start_str = url.query["start"]
        if start_str is None:
            return None
        return YoutubeURL._parse_time_string(start_str)

    @classmethod
    def from_url(cls, url: str) -> "YoutubeURL":
        parsed = cls._parse_url(url)
        video_id = cls._find_video_id(parsed)
        if not video_id:
            raise InvalidYoutubeUrlError("URL is not a valid youtube URL")
        start = cls._find_video_start(parsed)
        return YoutubeURL(video_id, start)

    def embed_obj(self, autoplay: Optional[bool] = None, origin: Optional[str] = None) -> URL:
        base = URL("https://www.youtube.com") / "embed" / self.video_id
        args = dict()
        if self.start:
            args["start"] = self.start
        if autoplay is not None:
            args["autoplay"] = "1" if autoplay else "0"
        if origin is not None:
            args["origin"] = origin
        return base.with_query(args)

    def link_obj(self) -> URL:
        base = URL(f"https://www.youtube.com") / "watch"
        args = dict(v=self.video_id)
        if self.start:
            args["start"] = str(self.start)
        return base.with_query(args)

    @property
    def embed_url(self) -> str:
        return str(self.embed_obj())

    @property
    def link_url(self) -> str:
        return str(self.link_obj())
