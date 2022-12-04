from typing import Optional
from urllib.parse import parse_qs, urlparse, urlsplit, urlunsplit

from django.conf import settings


def get_url(path):
    proto = "https://" if settings.SSL_ON else "http://"
    host = settings.DOMAIN
    return "{}{}{}".format(proto, host, path or "")


def get_url_local_path(url):
    parsed = urlsplit(url)
    newlist = ("", "", parsed[2], parsed[3], parsed[4])
    new = urlunsplit(newlist)
    return new


def parse_youtube_video_id(value: str) -> Optional[str]:
    if value.startswith("//"):
        query = urlparse(f"https:{value}")
    elif not value.startswith(("http://", "https://")):
        query = urlparse(f"https://{value}")
    else:
        query = urlparse(value)

    if query.hostname == "youtu.be":
        return query.path.split("/")[1]
    if query.hostname in ("www.youtube.com", "youtube.com"):
        if query.path == "/watch":
            p = parse_qs(query.query)
            if not p.get("v"):
                return None
            return p["v"][0]
        if query.path[:7] == "/embed/":
            return query.path.split("/")[2]
        if query.path[:3] == "/v/":
            return query.path.split("/")[2]
    return None
