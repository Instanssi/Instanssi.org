# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

def user_access_required(view_func):
    def _checklogin(request, *args, **kwargs):
        if request.user.is_authenticated() and request.user.is_active:
            return view_func(request, *args, **kwargs)
        event_id = kwargs.get('event_id')
        return HttpResponseRedirect(reverse('kompomaatti-login', args=(event_id,))) 
    return _checklogin
