# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import Http404,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from Instanssi.admin_base.misc.custom_render import admin_render

@login_required(login_url='/control/auth/login/')
def index(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Render response
    return admin_render(request, "admin_users/index.html", {})

@login_required(login_url='/control/auth/login/')
def openid(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Render response
    return admin_render(request, "admin_users/openid.html", {})