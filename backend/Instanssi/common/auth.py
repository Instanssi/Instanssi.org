from collections.abc import Callable
from functools import wraps
from typing import Any

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse

ViewFunc = Callable[..., HttpResponse]


def user_access_required(view_func: ViewFunc) -> ViewFunc:
    @wraps(view_func)
    def _checklogin(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated and request.user.is_active:
            return view_func(request, *args, **kwargs)
        return HttpResponseRedirect(reverse("account_login") + "?next=" + request.get_full_path())

    return _checklogin
