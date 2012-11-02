# -*- coding: utf-8 -*-

from common.http import Http403
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.ext_calendar.models import CalendarEvent
from Instanssi.admin_calendar.forms import CalendarEventForm

@login_required(login_url='/manage/auth/login/')
def index(request, sel_event_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
    
    # Handle form data
    if request.method == "POST":
        # Check rights
        if not request.user.has_perm('ext_calendar.add_calendarevent'):
            raise Http403
        
        # Handle form
        form = CalendarEventForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.save(commit=False)
            data.event_id = int(sel_event_id)
            data.user = request.user
            data.save()
            return HttpResponseRedirect("/manage/"+sel_event_id+"/calendar/")
    else:
        form = CalendarEventForm()
    
    # Filter calendar events by selected event
    cevs = CalendarEvent.objects.filter(event_id=int(sel_event_id))
    
    # Render response
    return admin_render(request, "admin_calendar/index.html", {
        'cevs': cevs,
        'selected_event_id': int(sel_event_id),
        'eventform': form,
        'LANGUAGE_CODE': getattr(settings, 'SHORT_LANGUAGE_CODE'),
    })

@login_required(login_url='/manage/auth/login/')
def edit(request, sel_event_id, cev_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
    
    # Check rights
    if not request.user.has_perm('ext_calendar.change_calendarevent'):
        raise Http403
    
    # Get calendarevent
    cev = get_object_or_404(CalendarEvent, pk=cev_id)
    
    # Handle form data
    if request.method == "POST":
        form = CalendarEventForm(request.POST, request.FILES, instance=cev)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/manage/"+sel_event_id+"/calendar/")
    else:
        form = CalendarEventForm(instance=cev)
    
    # Render response
    return admin_render(request, "admin_calendar/edit.html", {
        'eventform': form,
        'event': cev,
        'selected_event_id': int(sel_event_id),
        'LANGUAGE_CODE': getattr(settings, 'SHORT_LANGUAGE_CODE'),
    })
    
    
@login_required(login_url='/manage/auth/login/')
def delete(request, sel_event_id, cev_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
    
    # Check rights
    if not request.user.has_perm('ext_calendar.delete_calendarevent'):
        raise Http403
    
    # Handle delete
    try:
        CalendarEvent.objects.get(id=cev_id).delete()
    except:
        pass
    
    # Render response
    return HttpResponseRedirect("/manage/"+sel_event_id+"/calendar/")
    