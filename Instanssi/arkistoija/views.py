# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect, HttpResponse
from Instanssi import settings
import Instanssi.kompomaatti.models as kmodels
import Instanssi.arkisto.models as amodels
from forms import EventForm

def dummy(request):
    return {}

def handle_event(request):
    form = EventForm()
    return {'eventform': form}

def index(request, pgnum = "0"):
    # Make sure the user is admin
    if not request.user.is_authenticated() or not request.user.is_superuser:
        raise Http404
    
    # Set session stuff
    if not request.session.has_key('arkistoija') or len(request.session['arkistoija']) == 0:
        request.session['arkistoija'] = {
            'maxpage': 0,
            'event': {},
        }
    
    # Structure
    pages_nm = {
        0: 'arkistoija/index.html',
        1: 'arkistoija/event_settings.html',
    }
    pages_fx = {
        0: dummy,
        1: handle_event,
    }
    
    # Find template that we want to load
    pgidx = int(pgnum)
    if pgidx >= len(pages_nm):
        raise Http404
    
    # Prevent user from getting too far without passing through
    # all forms
    if pgidx > request.session['arkistoija']['maxpage']+1:
        raise Http404
    
    # Set max page
    if pgidx > request.session['arkistoija']['maxpage']:
        request.session['arkistoija']['maxpage'] = pgidx
    
    # Call our handler
    ext = pages_fx[pgidx](request)
    
    # Other vars
    vars = {
        'page_this': pgidx,
        'page_next': pgidx+1,
        'page_prev': pgidx-1,
    }
    return render_to_response(pages_nm[pgidx], dict(ext.items() + vars.items()))

def cancel(request):
    # Make sure the user is admin
    if not request.user.is_authenticated() or not request.user.is_superuser:
        raise Http404
    
    # Clear data
    request.session['arkistoija'] = {}
    
    # Redirect after cancellation
    return HttpResponseRedirect("/arkistoija/")

