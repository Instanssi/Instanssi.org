from urllib.parse import urlsplit, urlunsplit


def get_url_local_path(url: str) -> str:
    parsed = urlsplit(url)
    return urlunsplit(("", "", parsed[2], parsed[3], parsed[4]))
