# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, get_object_or_404
from Instanssi.kompomaatti.models import Event, Compo, Entry
from Instanssi.kompomaatti.misc import entrysort
from Instanssi.arkisto.models import OtherVideoCategory, OtherVideo
from django.template import RequestContext
from django.http import Http404, HttpResponse
from django.conf import settings

# Event page
def event(request, event_id):
    # Get event
    event = get_object_or_404(Event, pk=int(event_id), archived=True)
    
    # Get all compos that are active but not hidden from archive
    compos = Compo.objects.filter(event=event, active=True, hide_from_archive=False)
    compolist = []
    for compo in compos:
        if compo.show_voting_results:
            compo.entries = entrysort.sort_by_score(Entry.objects.filter(compo=compo))
        else:
            compo.entries = Entry.objects.filter(compo=compo).order_by('name')
        compolist.append(compo)
        
    # Get other videos
    cats = OtherVideoCategory.objects.filter(event=event).order_by('name')
    videolist = []
    for cat in cats:
        cat.videos = OtherVideo.objects.filter(category=cat)
        videolist.append(cat)
    
    # Render Event frontpage
    return render_to_response('arkisto/index.html', {
        'event': event,
        'compos': compolist,
        'videos': videolist,
    }, context_instance=RequestContext(request))

# Index page (loads event page)
def index(request):
    try:
        latest = Event.objects.filter(archived=True).latest('date')
    except:
        return render_to_response('arkisto/empty.html', context_instance=RequestContext(request))
            
    return event(request, latest.id)

# Entry page
def entry(request, entry_id):
    # Get the entry
    entry = get_object_or_404(Entry, pk=entry_id)

    # Make sure the entry belongs to an archived event
    if not entry.compo.event.archived:
        raise Http404
    
    # Make sure the compo is active and can be shown
    if entry.compo.hide_from_archive or not entry.compo.active:
        raise Http404
    
    # Dump the page
    return render_to_response('arkisto/entry.html', {
        'entry': entry,
        'event': entry.compo.event,
    }, context_instance=RequestContext(request))
    
# Video page
def video(request, video_id):
    # Get the entry
    video = get_object_or_404(OtherVideo, pk=video_id)

    # Make sure the entry belongs to an archived event
    if not video.category.event.archived:
        raise Http404
    
    # Dump the page
    return render_to_response('arkisto/video.html', {
        'video': video,
        'event': video.category.event,
    }, context_instance=RequestContext(request))
    
