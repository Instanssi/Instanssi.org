# -*- coding: utf-8 -*-

from common.http import Http403
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.admin_base.misc.auth_decorator import su_access_required

@su_access_required
def diskcleaner(request):
    # Render response
    return admin_render(request, "admin_utils/diskcleaner.html", {
    })
    
@su_access_required
def log(request):
    # Render response
    return admin_render(request, "admin_utils/log.html", {
    })