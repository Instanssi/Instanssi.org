def size_format(size: int) -> str:
    kb = 1024
    mb = kb * 1024
    gb = mb * 1024
    if size > gb:
        return f"{round(size / gb, 2)} Gt"
    if size > mb:
        return f"{round(size / mb, 2)} Mt"
    if size > kb:
        return f"{round(size / kb, 2)} Kt"
    return f"{size} t"
