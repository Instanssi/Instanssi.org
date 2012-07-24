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
    return render_to_response("admin_kompomaatti/index.html", {
    }, context_instance=RequestContext(request))
    
@login_required(login_url='/control/auth/login/')
def compos(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Render response
    return render_to_response("admin_kompomaatti/index.html", {
    }, context_instance=RequestContext(request))
    
@login_required(login_url='/control/auth/login/')
def entries(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Render response
    return render_to_response("admin_kompomaatti/index.html", {
    }, context_instance=RequestContext(request))
    
@login_required(login_url='/control/auth/login/')
def results(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Render response
    return render_to_response("admin_kompomaatti/index.html", {
    }, context_instance=RequestContext(request))
    
@login_required(login_url='/control/auth/login/')
def votecodes(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Render response
    return render_to_response("admin_kompomaatti/index.html", {
    }, context_instance=RequestContext(request))
    
@login_required(login_url='/control/auth/login/')
def votecoderequests(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Render response
    return render_to_response("admin_kompomaatti/index.html", {
    }, context_instance=RequestContext(request))