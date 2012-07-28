# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import Http404,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from Instanssi.dbsettings.models import Setting
from Instanssi.kompomaatti.models import Compo,Entry,VoteCodeRequest
from Instanssi.admin_kompomaatti.forms import AdminCompoForm, AdminEntryForm, AdminEntryAddForm
from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.admin_base.misc.eventsel import get_selected_event
from Instanssi.kompomaatti.misc import entrysort
    
@login_required(login_url='/control/auth/login/')
def compo_browse(request):
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
    return admin_render(request, "admin_kompomaatti/compo_browse.html", {
        'compos': compos,
        'compoform': compoform,
    })
    
@login_required(login_url='/control/auth/login/')
def compo_add(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Get compos
    selected_event_id = get_selected_event(request)
    
    # Form handling
    if request.method == "POST":
        compoform = AdminCompoForm(request.POST)
        if compoform.is_valid():
            data = compoform.save(commit=False)
            data.event_id = selected_event_id
            data.save()
            return HttpResponseRedirect('/control/kompomaatti/compos/') 
    else:
        compoform = AdminCompoForm()
    
    # Render response
    return admin_render(request, "admin_kompomaatti/compo_add.html", {
        'compoform': compoform,
    })
    
@login_required(login_url='/control/auth/login/')
def compo_edit(request, compo_id):
    # Make sure the user is staff.index.html
    if not request.user.is_staff:
        raise Http404
    
    # Check ID
    try:
        compo = Compo.objects.get(id=compo_id)
    except:
        raise Http404
    
    # Handle form
    if request.method == "POST":
        editform = AdminCompoForm(request.POST, instance=compo)
        if editform.is_valid():
            editform.save()
            return HttpResponseRedirect('/control/kompomaatti/entries/') 
    else:
        editform = AdminCompoForm(instance=compo)
    
    # Render response
    return admin_render(request, "admin_kompomaatti/compo_edit.html", {
        'compo': compo,
        'editform': editform,
    })
    
@login_required(login_url='/control/auth/login/')
def entry_browse(request):
    # Make sure the user is staff.index.html
    if not request.user.is_staff:
        raise Http404
    
    # Get Entries    
    selected_event_id = get_selected_event(request)
    compos = Compo.objects.filter(event=selected_event_id)
    entries = Entry.objects.filter(compo__in=compos)
    
    # Render response
    return admin_render(request, "admin_kompomaatti/entry_browse.html", {
        'entries': entries,
    })
    
@login_required(login_url='/control/auth/login/')
def entry_edit(request, entry_id):
    # Make sure the user is staff.index.html
    if not request.user.is_staff:
        raise Http404
    
    # Check ID
    try:
        entry = Entry.objects.get(id=entry_id)
    except:
        raise Http404
    
    # Handle form
    if request.method == "POST":
        editform = AdminEntryForm(request.POST, request.FILES, instance=entry)
        if editform.is_valid():
            editform.save()
            return HttpResponseRedirect('/control/kompomaatti/entries/') 
    else:
        editform = AdminEntryForm(instance=entry)
    
    # Render response
    return admin_render(request, "admin_kompomaatti/entry_edit.html", {
        'entry': entry,
        'editform': editform,
    })
    
@login_required(login_url='/control/auth/login/')
def entry_add(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Get compos
    selected_event_id = get_selected_event(request)
    
    # Form handling
    if request.method == "POST":
        entryform = AdminEntryAddForm(request.POST, request.FILES)
        if entryform.is_valid():
            data = entryform.save(commit=False)
            data.event_id = selected_event_id
            data.save()
            return HttpResponseRedirect('/control/kompomaatti/entries/') 
    else:
        entryform = AdminEntryAddForm()
    
    # Render response
    return admin_render(request, "admin_kompomaatti/entry_add.html", {
        'entryform': entryform,
    })
    
@login_required(login_url='/control/auth/login/')
def results(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Get compos
    selected_event_id = get_selected_event(request)
    try:
        compos = Compo.objects.filter(event_id=selected_event_id)
    except Entry.DoesNotExist:
        raise Http404
    
    # Get the entries
    results = {}
    for compo in compos:
        results[compo.name] = entrysort.sort_by_score(Entry.objects.filter(compo=compo))
    
    print results
    
    # Render response
    return admin_render(request, "admin_kompomaatti/results.html", {
        'results': results,
    })
    
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
