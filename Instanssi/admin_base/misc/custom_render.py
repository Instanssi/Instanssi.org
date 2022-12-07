from typing import Dict, Optional

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def admin_render(request: HttpRequest, tpl: str, context: Optional[Dict] = None) -> HttpResponse:
    if not context:
        context = {}
    return render(request, tpl, context)
