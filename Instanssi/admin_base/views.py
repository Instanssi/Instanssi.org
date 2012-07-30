# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from Instanssi.admin_base.misc.eventsel import get_selected_event

@login_required(login_url='/control/auth/login/')
def index(request):
    # Select latest event as default
    print get_selected_event(request)
    
    # Redirect to events page
    return HttpResponseRedirect("/control/events/")
    
@login_required(login_url='/control/auth/login/')
def eventchange(request, event_id):
    # Get redirect path
    if 'r' in request.GET:
        r = request.GET['r']
        if r[0] != "/":
            r = "/control/"
    else:
        r = "/control/"
        
    # Set session variable
    try:
        request.session['m_event_id'] = int(event_id)
    except:
        raise Http404
        
    # Redirect
    return HttpResponseRedirect(r)