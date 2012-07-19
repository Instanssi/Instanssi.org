# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from Instanssi.kompomaatti.models import Compo, Entry
from Instanssi.kompomaatti.misc import entrysort

@login_required(login_url='/control/auth/login/')
def index(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Render response
    return render_to_response("admin_slides/index.html", {
        'compos': Compo.objects.all(),
    }, context_instance=RequestContext(request))
    
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
    return render_to_response('admin_slides/slide_results.html', {
        'entries': entries,
        'compo': c,
    }, context_instance=RequestContext(request))
    
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
    return render_to_response('admin_slides/slide_entries.html', {
        'entries': entries,
        'compo': c,
    }, context_instance=RequestContext(request))
    
