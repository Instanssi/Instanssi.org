from django.http import HttpResponseRedirect
from django.urls import reverse

from Instanssi.common.http import Http403


def user_access_required(view_func):
    def _checklogin(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_active:
            return view_func(request, *args, **kwargs)
        return HttpResponseRedirect(reverse("users:login") + "?next=" + request.get_full_path())

    return _checklogin


def staff_access_required(view_func):
    def _checklogin(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_active:
            if request.user.is_staff:
                return view_func(request, *args, **kwargs)
            raise Http403
        return HttpResponseRedirect(reverse("users:login") + "?next=" + request.get_full_path())

    return _checklogin


def su_access_required(view_func):
    def _checklogin(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_active:
            if request.user.is_staff and request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            raise Http403
        return HttpResponseRedirect(reverse("users:login") + "?next=" + request.get_full_path())

    return _checklogin


def infodesk_access_required(view_func):
    def _checklogin(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_active:
            if request.user.has_perm("store.change_storetransaction"):
                return view_func(request, *args, **kwargs)
            raise Http403
        return HttpResponseRedirect(reverse("users:login") + "?next=" + request.get_full_path())

    return _checklogin
