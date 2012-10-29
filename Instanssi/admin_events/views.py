# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import Http404,HttpResponseRedirect,HttpResponse
from django.contrib.auth.decorators import login_required
from Instanssi.kompomaatti.models import Event
from Instanssi.admin_events.forms import EventForm
from Instanssi.admin_base.misc.custom_render import admin_render

@login_required(login_url='/manage/auth/login/')
def index(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Get all events
    events = Event.objects.all()
    
    # Render response
    return admin_render(request, "admin_events/index.html", {
        'events': events,
    })

@login_required(login_url='/manage/auth/login/')
def add(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Check for permissions
    if not request.user.has_perm('kompomaatti.add_event'):
        raise Http404
    
    # Handle form data, if any
    if request.method == 'POST':
        eventform = EventForm(request.POST)
        if eventform.is_valid():
            data = eventform.save(commit=False)
            data.archived = False
            data.save()
            return HttpResponseRedirect("/manage/events/")
    else:
        eventform = EventForm()
    
    # Render response
    return admin_render(request, "admin_events/add.html", {
        'eventform': eventform,
    })

@login_required(login_url='/manage/auth/login/')
def edit(request, event_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Check for permissions
    if not request.user.has_perm('kompomaatti.change_event'):
        raise Http404
    
    # Get event, or show 404 if it doesn't exist
    try:
        event = Event.objects.get(id=event_id)
    except:
        raise Http404
    
    # Handle form data, if any
    if request.method == 'POST':
        eventform = EventForm(request.POST, instance=event)
        if eventform.is_valid():
            data = eventform.save(commit=False)
            data.archived = False
            data.save()
            return HttpResponseRedirect("/manage/events/")
    else:
        eventform = EventForm(instance=event)
    
    # Render response
    return admin_render(request, "admin_events/edit.html", {
        'eventform': eventform,
    })

@login_required(login_url='/manage/auth/login/')
def delete(request, event_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Check for permissions
    if not request.user.has_perm('kompomaatti.delete_event'):
        raise Http404
    
    # Delete the file
    try:
        Event.objects.get(id=event_id).delete()
    except:
        pass
    
    return HttpResponseRedirect("/manage/events/")
