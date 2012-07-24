# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import Http404,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from Instanssi.dbsettings.models import Setting
from Instanssi.kompomaatti.models import Compo,Entry,VoteCodeRequest
from Instanssi.admin_kompomaatti.forms import AdminCompoForm, AdminEntryForm

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
    
    # Get compos
    active_event_id = Setting.get('active_event_id', 'events', -1)
    compos = Compo.objects.filter(event=active_event_id)
    
    # Form handling
    if request.method == "POST":
        compoform = AdminCompoForm(request.POST)
        if compoform.is_valid():
            data = compoform.save(commit=False)
            data.event_id = active_event_id
            data.save()
            return HttpResponseRedirect('/control/kompomaatti/compos/') 
    else:
        compoform = AdminCompoForm()
    
    # Render response
    return render_to_response("admin_kompomaatti/compos.html", {
        'compos': compos,
        'compoform': compoform,
    }, context_instance=RequestContext(request))
    
@login_required(login_url='/control/auth/login/')
def entries(request):
    # Make sure the user is staff.index.html
    if not request.user.is_staff:
        raise Http404
    
    # Get Entries    
    active_event_id = Setting.get('active_event_id', 'events', -1)
    compos = Compo.objects.filter(event=active_event_id)
    entries = Entry.objects.filter(compo__in=compos)
    
    # Form handling
    entryform = AdminEntryForm()
    
    # Render response
    return render_to_response("admin_kompomaatti/entries.html", {
        'entries': entries,
        'entryform': entryform,
    }, context_instance=RequestContext(request))
    
@login_required(login_url='/control/auth/login/')
def results(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Render response
    return render_to_response("admin_kompomaatti/results.html", {
    }, context_instance=RequestContext(request))
    
@login_required(login_url='/control/auth/login/')
def votecodes(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Render response
    return render_to_response("admin_kompomaatti/votecodes.html", {
    }, context_instance=RequestContext(request))
    
@login_required(login_url='/control/auth/login/')
def votecoderequests(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    requests = VoteCodeRequest.objects.all()
    
    # Render response
    return render_to_response("admin_kompomaatti/vcrequests.html", {
        'requests': requests,
    }, context_instance=RequestContext(request))