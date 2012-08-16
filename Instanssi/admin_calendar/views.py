# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import Http404,HttpResponseRedirect,HttpResponse
from django.contrib.auth.decorators import login_required
from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.ext_calendar.models import CalendarEvent
from Instanssi.admin_base.misc.eventsel import get_selected_event
from Instanssi.admin_calendar.forms import CalendarEventForm

@login_required(login_url='/control/auth/login/')
def index(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Filter calendar events by selected event
    cevs = CalendarEvent.objects.filter(event_id=get_selected_event(request))
    
    # Render response
    return admin_render(request, "admin_calendar/index.html", {
        'cevs': cevs,
    })

@login_required(login_url='/control/auth/login/')
def add(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Check rights
    if not request.user.has_perm('ext_calendar.add_calendarevent'):
        raise Http404
    
    # Handle form data
    if request.method == "POST":
        form = CalendarEventForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.save(commit=False)
            data.event_id = get_selected_event(request)
            data.user = request.user
            data.save()
            return HttpResponseRedirect("/control/calendar/")
    else:
        form = CalendarEventForm()
    
    # Render response
    return admin_render(request, "admin_programme/add.html", {
        'eventform': form,
    })

@login_required(login_url='/control/auth/login/')
def edit(request, cev_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Check rights
    if not request.user.has_perm('ext_calendar.change_calendarevent'):
        raise Http404
    
    # Get calendarevent
    try:
        cev = CalendarEvent.objects.get(id=cev_id)
    except:
        raise Http404
    
    # Handle form data
    if request.method == "POST":
        form = CalendarEventForm(request.POST, request.FILES, instance=cev)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/control/calendar/")
    else:
        form = CalendarEventForm(instance=cev)
    
    # Render response
    return admin_render(request, "admin_programme/edit.html", {
        'eventform': form,
        'event': cev,
    })
    
    
@login_required(login_url='/control/auth/login/')
def delete(request, cev_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Check rights
    if not request.user.has_perm('ext_calendar.delete_calendarevent'):
        raise Http404
    
    # Handle delete
    try:
        CalendarEvent.objects.get(id=cev_id).delete()
    except:
        raise Http404
    
    # Render response
    return HttpResponseRedirect("/control/calendar/")
    