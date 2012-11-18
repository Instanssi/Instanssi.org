# -*- coding: utf-8 -*-

from common.http import Http403
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse
from django.core.urlresolvers import reverse
from Instanssi.kompomaatti.models import Event
from Instanssi.admin_events.forms import EventForm
from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.admin_base.misc.auth_decorator import staff_access_required

# Logging related
import logging
logger = logging.getLogger(__name__)

@staff_access_required
def index(request):
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
            logger.info('Event "'+data.name+'" added.', extra={'user': request.user})
            return HttpResponseRedirect(reverse('manage-events:index'))
    else:
        eventform = EventForm()
    
    # Get all events
    events = Event.objects.all()
    
    # Render response
    return admin_render(request, "admin_events/index.html", {
        'events': events,
        'eventform': eventform,
    })

@staff_access_required
def edit(request, event_id):
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
            logger.info('Event "'+data.name+'" edited.', extra={'user': request.user})
            return HttpResponseRedirect(reverse('manage-events:index'))
    else:
        eventform = EventForm(instance=event)
    
    # Render response
    return admin_render(request, "admin_events/edit.html", {
        'eventform': eventform,
    })

@staff_access_required
def delete(request, event_id):
    # Check for permissions
    if not request.user.has_perm('kompomaatti.delete_event'):
        raise Http403
    
    # Delete the file
    try:
        event = Event.objects.get(id=event_id)
        event.delete()
        logger.info('Event "'+event.name+'" deleted.', extra={'user': request.user})
    except:
        pass
    
    return HttpResponseRedirect(reverse('manage-events:index'))
