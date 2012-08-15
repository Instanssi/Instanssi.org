# -*- coding: utf-8 -*-

from django.http import Http404,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.ext_programme.models import ProgrammeEvent
from Instanssi.admin_base.misc.eventsel import get_selected_event
from Instanssi.admin_programme.forms import ProgrammeEventForm

@login_required(login_url='/control/auth/login/')
def index(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Filter programme events by selected event
    pevs = ProgrammeEvent.objects.filter(event_id=get_selected_event(request))
    
    # Render response
    return admin_render(request, "admin_programme/index.html", {
        'pevs': pevs,
    })

@login_required(login_url='/control/auth/login/')
def add(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Check rights
    if not request.user.has_perm('ext_programme.add_programmeevent'):
        raise Http404
    
    # Create form
    if request.method == "POST":
        form = ProgrammeEventForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.save(commit=False)
            data.event_id = get_selected_event(request)
            data.save()
            return HttpResponseRedirect("/control/programme/")
    else:
        form = ProgrammeEventForm()
    
    # Render response
    return admin_render(request, "admin_programme/add.html", {
        'eventform': form,
    })

@login_required(login_url='/control/auth/login/')
def edit(request, pev_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Check rights
    if not request.user.has_perm('ext_programme.change_programmeevent'):
        raise Http404
    
    # Get event
    try:
        pev = ProgrammeEvent.objects.get(id=pev_id)
    except:
        raise Http404
    
    # Create form
    if request.method == "POST":
        form = ProgrammeEventForm(request.POST, request.FILES, instance=pev)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/control/programme/")
    else:
        form = ProgrammeEventForm(instance=pev)
    
    # Render response
    return admin_render(request, "admin_programme/edit.html", {
        'eventform': form,
        'event': pev,
    })

@login_required(login_url='/control/auth/login/')
def delete(request, pev_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Check rights
    if not request.user.has_perm('ext_programme.delete_programmeevent'):
        raise Http404
    
    # Delete event
    try:
        ProgrammeEvent.objects.get(id=pev_id).delete()
    except:
        raise Http404
    
    # Render response
    return HttpResponseRedirect("/control/programme/")

