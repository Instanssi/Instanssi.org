# -*- coding: utf-8 -*-

from django.conf import settings
from django.http import HttpResponseRedirect
from common.http import Http403

def staff_access_required(view_func):
    def _checklogin(request, *args, **kwargs):
        if request.user.is_authenticated() and request.user.is_active:
            if request.user.is_staff:
                return view_func(request, *args, **kwargs)
            raise Http403
        return HttpResponseRedirect(getattr(settings, 'ADMIN_LOGIN_URL')) 
    return _checklogin

def su_access_required(view_func):
    def _checklogin(request, *args, **kwargs):
        if request.user.is_authenticated() and request.user.is_active:
            if request.user.is_staff and request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            raise Http403
        return HttpResponseRedirect(getattr(settings, 'ADMIN_LOGIN_URL')) 
    return _checklogin