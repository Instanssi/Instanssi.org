from typing import Any, NoReturn

from django.http import Http404, HttpRequest


def dummy_index(request: HttpRequest, *args: Any, **kwargs: Any) -> NoReturn:
    """
    This just returns 404. Normally we would see new kompomaatti UI due to nginx redirect, so this is here
    only so that we can retain the natural redirects from urls.py.
    """
    raise Http404()
