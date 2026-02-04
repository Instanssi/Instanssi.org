from collections.abc import Callable
from typing import Any

EndpointType = tuple[str, str, str, Callable[..., Any]]


def preprocessor_hook(endpoints: list[EndpointType]) -> list[EndpointType]:
    """This is used to restrict drf-spectacular to only v2 entrypoints"""
    filtered: list[EndpointType] = []
    for path, path_regex, method, callback in endpoints:
        if path.startswith("/api/v2"):
            filtered.append((path, path_regex, method, callback))
    return filtered
