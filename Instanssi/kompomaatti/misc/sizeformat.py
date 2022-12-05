def size_format(size: int) -> str:
    kb = 1024
    mb = kb * 1024
    gb = mb * 1024
    if size > gb:
        return "{} Gt".format(round(size / gb, 2))
    if size > mb:
        return "{} Mt".format(round(size / mb, 2))
    if size > kb:
        return "{} Kt".format(round(size / kb, 2))
    return "{} t".format(size)
