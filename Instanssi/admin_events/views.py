# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import Http404,HttpResponseRedirect,HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from Instanssi.kompomaatti.models import Event
from Instanssi.admin_events.forms import EventForm
from common.responses import JSONResponse

@login_required(login_url='/control/auth/login/')
def index(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Get all events
    events = Event.objects.all()
    form = EventForm()
    
    # Render response
    return render_to_response("admin_events/index.html", {
        'events': events,
        'eventform': form,
    }, context_instance=RequestContext(request))

@login_required(login_url='/control/auth/login/')
def settings(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Render response
    return render_to_response("admin_events/settings.html", {
    }, context_instance=RequestContext(request))

@login_required(login_url='/control/auth/login/')
def edit(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Render response
    return render_to_response("admin_events/edit.html", {
    }, context_instance=RequestContext(request))

def json_delete(request):
    if not request.user.is_authenticated() or not request.user.is_staff:
        return JSONResponse({'error': 'Not authenticated!'})
    output = {'error': ''}
    


    return JSONResponse(output)
