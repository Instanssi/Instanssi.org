# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import Http404,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from Instanssi.dbsettings.models import Setting
from Instanssi.kompomaatti.models import Compo,Entry,VoteCodeRequest
from Instanssi.admin_kompomaatti.forms import AdminCompoForm, AdminEntryForm
from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.admin_base.misc.eventsel import get_selected_event
    
@login_required(login_url='/control/auth/login/')
def compos(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Get compos
    selected_event_id = get_selected_event(request)
    compos = Compo.objects.filter(event=selected_event_id)
    
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
    return admin_render(request, "admin_kompomaatti/compos.html", {
        'compos': compos,
        'compoform': compoform,
    })
    
@login_required(login_url='/control/auth/login/')
def entries(request):
    # Make sure the user is staff.index.html
    if not request.user.is_staff:
        raise Http404
    
    # Get Entries    
    selected_event_id = get_selected_event(request)
    compos = Compo.objects.filter(event=selected_event_id)
    entries = Entry.objects.filter(compo__in=compos)
    
    # Render response
    return admin_render(request, "admin_kompomaatti/entries.html", {
        'entries': entries,
    })
    
@login_required(login_url='/control/auth/login/')
def results(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Render response
    return admin_render("admin_kompomaatti/results.html", {})
    
@login_required(login_url='/control/auth/login/')
def votecodes(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Render response
    return admin_render(request, "admin_kompomaatti/votecodes.html", {})
    
@login_required(login_url='/control/auth/login/')
def votecoderequests(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    requests = VoteCodeRequest.objects.all()
    
    # Render response
    return admin_render(request, "admin_kompomaatti/vcrequests.html", {
        'requests': requests,
    })
