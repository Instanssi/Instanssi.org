# -*- coding: utf-8 -*-

from common.http import Http403
from common.responses import JSONResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, Http404
from Instanssi.infodesk.misc.auth_decorator import infodesk_access_required
from Instanssi.infodesk.forms import KeyScanForm
    
@infodesk_access_required
def index(request):
    return render_to_response('infodesk/index.html', {}, context_instance=RequestContext(request))

@infodesk_access_required
def ticket_check(request):
    if request.method == 'POST':
        form = KeyScanForm(request.POST)
        if form.is_valid():
            pass
    else:
        form = KeyScanForm()
    
    return render_to_response('infodesk/ticket_check.html', {'form': form}, context_instance=RequestContext(request))

@infodesk_access_required
def store_check(request):
    if request.method == 'POST':
        form = KeyScanForm(request.POST)
        if form.is_valid():
            pass
    else:
        form = KeyScanForm()
    
    return render_to_response('infodesk/store_check.html', {'form': form}, context_instance=RequestContext(request))

@infodesk_access_required
def ticket_info(request, ticket_id):
    return render_to_response('infodesk/ticket_info.html', {}, context_instance=RequestContext(request))

@infodesk_access_required
def store_info(request, transaction_id):
    return render_to_response('infodesk/store_info.html', {}, context_instance=RequestContext(request))
