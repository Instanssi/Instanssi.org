# -*- coding: utf-8 -*-

from Instanssi.common.http import Http403
from Instanssi.common.auth import staff_access_required
from django.http import Http404,HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.conf import settings
from Instanssi.ext_programme.models import ProgrammeEvent
from Instanssi.admin_programme.forms import ProgrammeEventForm
from Instanssi.admin_base.misc.custom_render import admin_render

# Logging related
import logging
logger = logging.getLogger(__name__)


@staff_access_required
def index(request, sel_event_id):
    # Create form
    if request.method == "POST":
        # Check rights
        if not request.user.has_perm('ext_programme.add_programmeevent'):
            raise Http403
        
        # Handle form
        form = ProgrammeEventForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.save(commit=False)
            data.event_id = int(sel_event_id)
            data.save()
            logger.info('Programme event "{}" added.'.format(data.title),
                        extra={'user': request.user, 'event_id': sel_event_id})
            return HttpResponseRedirect(reverse('manage-programme:index', args=(sel_event_id, )))
    else:
        form = ProgrammeEventForm()
    
    # Filter programme events by selected event
    pevs = ProgrammeEvent.objects.filter(event_id=int(sel_event_id))
    
    # Render response
    return admin_render(request, "admin_programme/index.html", {
        'pevs': pevs,
        'selected_event_id': int(sel_event_id),
        'eventform': form,
    })


@staff_access_required
def edit(request, sel_event_id, pev_id):
    # Check rights
    if not request.user.has_perm('ext_programme.change_programmeevent'):
        raise Http403
    
    # Get event
    pev = get_object_or_404(ProgrammeEvent, pk=pev_id)
    
    # Create form
    if request.method == "POST":
        form = ProgrammeEventForm(request.POST, request.FILES, instance=pev)
        if form.is_valid():
            data = form.save()
            logger.info('Programme event "{}" edited.'.format(data.title),
                        extra={'user': request.user, 'event_id': sel_event_id})
            return HttpResponseRedirect(reverse('manage-programme:index', args=(sel_event_id, )))
    else:
        form = ProgrammeEventForm(instance=pev)
    
    # Render response
    return admin_render(request, "admin_programme/edit.html", {
        'eventform': form,
        'event': pev,
        'selected_event_id': int(sel_event_id),
    })


@staff_access_required
def delete(request, sel_event_id, pev_id):
    # Check rights
    if not request.user.has_perm('ext_programme.delete_programmeevent'):
        raise Http403
    
    # Delete event
    try:
        p = ProgrammeEvent.objects.get(id=pev_id)
        p.delete()
        logger.info('Programme event "{}" deleted.'.format(p.title),
                    extra={'user': request.user, 'event_id': sel_event_id})
    except:
        raise Http404
    
    # Render response
    return HttpResponseRedirect(reverse('manage-programme:index', args=(sel_event_id, )))

