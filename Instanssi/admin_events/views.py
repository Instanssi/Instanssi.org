# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import Http404,HttpResponseRedirect,HttpResponse
from django.contrib.auth.decorators import login_required
from Instanssi.kompomaatti.models import Event
from Instanssi.admin_events.forms import EventForm
from Instanssi.dbsettings.forms import SettingForm
from common.responses import JSONResponse
from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.admin_base.misc.eventsel import get_selected_event

@login_required(login_url='/control/auth/login/')
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

@login_required(login_url='/control/auth/login/')
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
            return HttpResponseRedirect("/control/events/")
    else:
        eventform = EventForm()
    
    # Render response
    return admin_render(request, "admin_events/add.html", {
        'eventform': eventform,
    })


@login_required(login_url='/control/auth/login/')
def settings(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Choices
    choices = {
        'active_event_id': [
            (-1, u'Ei mitään'),
        ],
    }
    for event in Event.objects.all():
        choices['active_event_id'].append((event.id, event.name))
    
    # Create settingsform OR handle save
    if request.method == 'POST':
        settingform = SettingForm(request.POST, group=u'events', choices=choices)
        if settingform.is_valid():
            settingform.save()
            return HttpResponseRedirect("/control/events/settings/")
    else:
        settingform = SettingForm(group=u'events', choices=choices)
        
    # Set titles & descriptions
    settingform.set_label('active_event_id', u'Aktiivinen tapahtuma')
    settingform.set_help_text('active_event_id', u'Kompomaatissa tällä hetkellä aktiivinen tapahtuma')
    
    # Render response
    return admin_render(request, "admin_events/settings.html", {
        'settingform': settingform,
    })

@login_required(login_url='/control/auth/login/')
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
            return HttpResponseRedirect("/control/events/")
    else:
        eventform = EventForm(instance=event)
    
    # Render response
    return admin_render(request, "admin_events/edit.html", {
        'eventform': eventform,
    })

@login_required(login_url='/control/auth/login/')
def delete(request, event_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Check for permissions
    if not request.user.has_perm('kompomaatti.delete_event'):
        raise Http404
    
    # If we remove event that is selected, delete the session variable
    # and let the system select a new event automatically.
    if event_id == get_selected_event(request):
        del request.session['m_event_id']
    
    # Delete the file
    try:
        Event.objects.get(id=event_id).delete()
    except:
        pass
    
    return HttpResponseRedirect("/control/events/")
