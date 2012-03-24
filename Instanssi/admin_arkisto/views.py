# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import Http404,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from Instanssi.kompomaatti.models import Event

@login_required(login_url='/control/auth/login/')
def index(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    events = Event.objects.all()
    
    # Render response
    return render_to_response("admin_arkisto/index.html", {
        'events': events,
    }, context_instance=RequestContext(request))

@login_required(login_url='/control/auth/login/')
def archiver(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404

    # Render response
    return render_to_response("admin_arkisto/archiver.html", {
    }, context_instance=RequestContext(request))

@login_required(login_url='/control/auth/login/')
def addtool(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Render response
    return render_to_response("admin_arkisto/addtool.html", {
    }, context_instance=RequestContext(request))
