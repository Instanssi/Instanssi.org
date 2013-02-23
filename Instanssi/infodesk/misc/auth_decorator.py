# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from common.http import Http403

def infodesk_access_required(view_func):
    def _checklogin(request, *args, **kwargs):
        if request.user.is_authenticated() \
           and request.user.is_active \
           and request.user.has_perm('tickets.change_ticket') \
           and request.user.has_perm('store.change_storetransaction'):
            return view_func(request, *args, **kwargs)
        raise Http403
    return _checklogin
