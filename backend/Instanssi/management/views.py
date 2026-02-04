from pathlib import Path
from typing import Any

from django.http import HttpRequest, HttpResponse

CURRENT_DIR = Path(__file__).resolve(strict=True).parent


def management_index(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
    with open(CURRENT_DIR / "site" / "index.html", "rb") as fd:
        return HttpResponse(fd.read(), status=200, content_type="text/html")
