# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from Instanssi.kompomaatti.models import Event, Compo, Entry
from Instanssi.kompomaatti.misc import entrysort
from Instanssi.arkisto.models import OtherVideoCategory, OtherVideo
from django.template import RequestContext
from django.http import Http404, HttpResponse
from Instanssi import settings

# Helper function for rendering pages
def custom_render(request, tpl, context={}):
    internal = {
        'nav_events': Event.objects.filter(archived=True).order_by('date').reverse(),
        'debugmode': settings.DEBUG,
    }
    return render_to_response(tpl, dict(context.items() + internal.items()), context_instance=RequestContext(request))

# Event page
def event(request, event_id):
    try:
        event = Event.objects.get(id=event_id, archived=True)
    except Event.DoesNotExist:
        raise Http404
    
    # Get all compos that are active but not hidden from archive
    compos = Compo.objects.filter(event=event, active=True, hide_from_archive=False)
    compolist = []
    for compo in compos:
        compo.entries = entrysort.sort_by_score(Entry.objects.filter(compo=compo))
        compolist.append(compo)
        
    # Get other videos
    cats = OtherVideoCategory.objects.filter(event=event).order_by('name')
    videolist = []
    for cat in cats:
        cat.videos = OtherVideo.objects.filter(category=cat)
        videolist.append(cat)
    
    # Render Event frontpage
    return custom_render(request, 'arkisto/index.html', {
        'event': event,
        'compos': compolist,
        'videos': videolist,
    })

# Index page (loads event page)
def index(request):
    try:
        latest = Event.objects.filter(archived=True).order_by('date').reverse()[0]
    except:
        return HttpResponse("No content in archive!")
        
    return event(request, latest.id)

# Entry page
def entry(request, entry_id):
    # Get the entry
    try:
        entry = Entry.objects.get(id=entry_id)
    except Entry.DoesNotExist:
        raise Http404

    # Make sure the entry belongs to an archived event
    if not entry.compo.event.archived:
        raise Http404
    
    # Make sure the compo is active and can be shown
    if entry.compo.hide_from_archive or not entry.compo.active:
        raise Http404
    
    # Get entry rank
    entries = entrysort.sort_by_score(Entry.objects.filter(compo=entry.compo))
    n = 1
    for e in entries:
        if e.id == entry.id:
            entry.rank = n
        n += 1
    
    # Dump the page
    return custom_render(request, 'arkisto/entry.html', {
        'entry': entry,
        'event': entry.compo.event,
    })
    
# Video page
def video(request, video_id):
    # Get the entry
    try:
        video = OtherVideo.objects.get(id=video_id)
    except Entry.DoesNotExist:
        raise Http404

    # Make sure the entry belongs to an archived event
    if not video.category.event.archived:
        raise Http404
    
    # Dump the page
    return custom_render(request, 'arkisto/video.html', {
        'video': video,
        'event': video.category.event,
    })
    
