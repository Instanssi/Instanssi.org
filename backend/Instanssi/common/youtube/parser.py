from typing import Optional

from yarl import URL


class InvalidYoutubeUrlError(Exception):
    pass


class YoutubeURL:
    def __init__(self, video_id: str, start: Optional[int] = None) -> None:
        self.video_id: str = video_id
        self.start: Optional[int] = start

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
    def _find_video_start(url: URL) -> Optional[str]:
        if "t" in url.query:
            return url.query["t"]
        if "start" in url.query:
            return url.query["start"]
        return None

    @classmethod
    def from_url(cls, url: str) -> "YoutubeURL":
        url = cls._parse_url(url)
        video_id = cls._find_video_id(url)
        if not video_id:
            raise InvalidYoutubeUrlError("URL is not a valid youtube URL")
        start = cls._find_video_start(url)
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
            args["start"] = self.start
        return base.with_query(args)

    @property
    def embed_url(self) -> str:
        return str(self.embed_obj())

    @property
    def link_url(self) -> str:
        return str(self.link_obj())
