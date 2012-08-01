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
    s_entries = entrysort.sort_by_score(Entry.objects.filter(compo=c))
    
    i = 0
    rot = 0
    f_entries = []
    for entry in s_entries:
        f_entries.append({
            'id': entry.id,
            'creator': entry.creator,
            'name': entry.name,
            'score': entry.get_score(),
            'score_x': i * 2500,
            'score_y': 0,
            'score_z': i * 500,
            'score_rot_y': rot,
            'info_x': (i+1) * 2500,
            'info_y': 0,
            'info_z': (i+1) * 500,
            'info_rot_y': rot+10,
        })
        i = i + 2
        rot = rot + 20

    # Render
    return admin_render(request, 'admin_slides/slide_results.html', {
        'entries': f_entries,
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
    s_entries = entrysort.sort_by_score(Entry.objects.filter(compo=c))

    i = 0
    flip = False
    f_entries = []
    for entry in s_entries:
        if flip: g = 180
        else: g = 0
        f_entries.append({
            'id': entry.id,
            'creator': entry.creator,
            'name': entry.name,
            'x': 0,
            'y': -i * 2500,
            'z': 0,
            'rot_y': 0,
            'rot_x': g,
            'rot_z': 0,
        })
        i = i + 1
        flip = not flip

    # Render
    return admin_render(request, 'admin_slides/slide_entries.html', {
        'entries': f_entries,
        'compo': c,
    })
    
