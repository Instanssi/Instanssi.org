# -*- coding: utf-8 -*-

from common.http import Http403
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.conf import settings
from Instanssi.kompomaatti.models import Event
from Instanssi.admin_events.forms import EventForm
from Instanssi.admin_base.misc.custom_render import admin_render

@login_required(login_url=getattr(settings, 'ADMIN_LOGIN_URL'))
def index(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
    
    # Handle form data, if any
    if request.method == 'POST':
        # CHeck for permissions
        if not request.user.has_perm('kompomaatti.add_event'):
            raise Http403
    
        # Handle form
        eventform = EventForm(request.POST)
        if eventform.is_valid():
            data = eventform.save(commit=False)
            data.archived = False
            data.save()
            return HttpResponseRedirect(reverse('admin-events'))
    else:
        eventform = EventForm()
    
    # Get all events
    events = Event.objects.all()
    
    # Render response
    return admin_render(request, "admin_events/index.html", {
        'events': events,
        'eventform': eventform,
    })

@login_required(login_url=getattr(settings, 'ADMIN_LOGIN_URL'))
def edit(request, event_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
    
    # Check for permissions
    if not request.user.has_perm('kompomaatti.change_event'):
        raise Http403
    
    # Get event, or show 404 if it doesn't exist
    event = get_object_or_404(Event, pk=event_id)
    
    # Handle form data, if any
    if request.method == 'POST':
        eventform = EventForm(request.POST, instance=event)
        if eventform.is_valid():
            data = eventform.save(commit=False)
            data.archived = False
            data.save()
            return HttpResponseRedirect(reverse('admin-events'))
    else:
        eventform = EventForm(instance=event)
    
    # Render response
    return admin_render(request, "admin_events/edit.html", {
        'eventform': eventform,
    })

@login_required(login_url=getattr(settings, 'ADMIN_LOGIN_URL'))
def delete(request, event_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
    
    # Check for permissions
    if not request.user.has_perm('kompomaatti.delete_event'):
        raise Http403
    
    # Delete the file
    try:
        Event.objects.get(id=event_id).delete()
    except:
        pass
    
    return HttpResponseRedirect(reverse('admin-events'))
