# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from Instanssi.kompomaatti.models import Event, Compo, Entry
from django.template import RequestContext
from django.http import Http404
from Instanssi import settings

def custom_render(request, tpl, context={}):
    internal = {
        'nav_events': Event.objects.filter(archived=True).order_by('date'),
        'debugmode': settings.DEBUG,
    }
    return render_to_response(tpl, dict(context.items() + internal.items()), context_instance=RequestContext(request))


def index(request):
    return custom_render(request, 'arkisto/index.html')


def entry(request, entry_id):
    '''
    # Get the entry
    try:
        entry = Entry.objects.get(id=entry_id)
    except Entry.DoesNotExist:
        raise Http404
    
    # Make sure the entry belongs to an archived event
    if entry.compo.event.archived != True:
        raise Http404
    
    # Dump the page
    return custom_render(request, 'arkisto/entry.html', {
        'entry': entry,
    })
    '''
    return custom_render(request, 'arkisto/entry.html')
