# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import Http404,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

@login_required(login_url='/control/auth/login/')
def index(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Render response
    return render_to_response("admin_users/index.html", {
    }, context_instance=RequestContext(request))

@login_required(login_url='/control/auth/login/')
def openid(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Render response
    return render_to_response("admin_users/openid.html", {
    }, context_instance=RequestContext(request))