# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import Http404,HttpResponseRedirect,HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.utils import simplejson
from models import CalendarEvent
from Instanssi.kompomaatti.models import Compo

def JSONResponse(data):
    return HttpResponse(simplejson.dumps(data), mimetype='application/json')

@login_required(login_url='/control/auth/login/')
def index(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Render response
    return render_to_response("admin_calendar/index.html", {
    }, context_instance=RequestContext(request))

def api_events(request, event_name):
    if not request.user.is_authenticated() or not request.user.is_staff:
        return JSONResponse({'error': 'Not authenticated!'})
    
    output = {'error': ''}
    if event_name == "events":
        output['events'] = []
        
        compos = Compo.object.filter(active=True)
    
    return JSONResponse(output)
