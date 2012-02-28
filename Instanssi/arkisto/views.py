# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from Instanssi.kompomaatti.models import Event, Compo, Entry
from django.template import RequestContext
from django.http import Http404, HttpResponse
from Instanssi import settings

def custom_render(request, tpl, context={}):
    internal = {
        'nav_events': Event.objects.filter(archived=True).order_by('date').reverse(),
        'debugmode': settings.DEBUG,
    }
    return render_to_response(tpl, dict(context.items() + internal.items()), context_instance=RequestContext(request))

def event(request, event_id):
    try:
        event = Event.objects.get(id=event_id)
    except Event.NotFound:
        raise Http404
    
    compos = Compo.objects.filter(event=event)
    compolist = []
    for compo in compos:
        compo.entries = Entry.objects.filter(compo=compo)
        compolist.append(compo)
    
    return custom_render(request, 'arkisto/index.html', {
        'event': event,
        'compos': compolist,
    })


def index(request):
    try:
        latest = Event.objects.all().order_by('date').reverse()[0]
    except:
        return HttpResponse("No content in archive!")
        
    return event(request, latest.id)


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
