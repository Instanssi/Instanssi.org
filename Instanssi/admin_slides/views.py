# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import Http404
from django.contrib.auth.decorators import login_required
from Instanssi.kompomaatti.models import Compo, Entry
from Instanssi.kompomaatti.misc import entrysort
from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.admin_base.misc.eventsel import get_selected_event

@login_required(login_url='/control/auth/login/')
def index(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Render response
    return admin_render(request, "admin_slides/index.html", {
        'compos': Compo.objects.filter(event_id=get_selected_event(request)),
    })
    
@login_required(login_url='/control/auth/login/')
def slide_results(request, compo_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404

    # Get the compo
    try:
        c = Compo.objects.get(id=compo_id)
    except Entry.DoesNotExist:
        raise Http404
    
    # Get the entries
    entries = entrysort.sort_by_score(Entry.objects.filter(compo=c))

    # Render
    return admin_render(request, 'admin_slides/slide_results.html', {
        'entries': entries,
        'compo': c,
    })
    
@login_required(login_url='/control/auth/login/')
def slide_entries(request, compo_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404

    # Get the compo
    try:
        c = Compo.objects.get(id=compo_id)
    except Entry.DoesNotExist:
        raise Http404
    
    # Get the entries
    entries = entrysort.sort_by_score(Entry.objects.filter(compo=c))

    # Render
    return admin_render(request, 'admin_slides/slide_entries.html', {
        'entries': entries,
        'compo': c,
    })
    
