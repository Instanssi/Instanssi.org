# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import Http404,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.kompomaatti.models import Event
from Instanssi.arkisto.models import OtherVideo,OtherVideoCategory
from Instanssi.admin_base.misc.eventsel import get_selected_event

@login_required(login_url='/control/auth/login/')
def index(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    events = Event.objects.all()
    
    # Render response
    return admin_render(request, "admin_arkisto/index.html", {
        'events': events,
    })

@login_required(login_url='/control/auth/login/')
def archiver(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404

    # Render response
    return admin_render(request, "admin_arkisto/archiver.html", {})

@login_required(login_url='/control/auth/login/')
def othervids(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Get videos belonging to selected event
    selected_event_id = get_selected_event(request)
    categories = OtherVideoCategory.objects.filter(event_id=selected_event_id)
    videos = []
    for cat in categories:
        vlist = OtherVideo.objects.filter(category=cat)
        for video in vlist:
            videos.append(video)
    
    # Render response
    return admin_render(request, "admin_arkisto/othervids.html", {
        'videos': videos,
    })
