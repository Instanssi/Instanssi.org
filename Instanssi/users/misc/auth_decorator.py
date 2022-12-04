from django.http import HttpResponseRedirect
from django.urls import reverse


def user_access_required(view_func):
    def _checklogin(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_active:
            return view_func(request, *args, **kwargs)
        return HttpResponseRedirect(reverse("users:login"))

    return _checklogin
