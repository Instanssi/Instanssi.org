import yarl


def get_url_local_path(url: str) -> str:
    src = yarl.URL(url)
    dst = yarl.URL.build(path=src.path, query_string=src.query_string, fragment=src.fragment)
    return str(dst)
