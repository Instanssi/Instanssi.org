# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect, HttpResponse
from Instanssi import settings
import Instanssi.kompomaatti.models as kmodels
import Instanssi.arkisto.models as amodels

pages = (
    'arkistoija/index.html',
    'arkistoija/event_settings.html'
)

def index(request, pgnum = "0"):
    # Make sure the user is admin
    if not request.user.is_authenticated() or not request.user.is_superuser:
        raise Http404
    
    # Find template that we want to load
    pgidx = int(pgnum)
    tpl = pages[pgidx]
    
    # Display template
    return render_to_response(tpl, {
        'page_this': pgidx,
        'page_next': pgidx+1,
        'page_prev': pgidx-1,
    })

def cancel(request):
    # Make sure the user is admin
    if not request.user.is_authenticated() or not request.user.is_superuser:
        raise Http404
    
    # TODO: Cancelling the transfer op goes here
    
    # Redirect after cancellation
    return HttpResponseRedirect("/arkistoija/")

