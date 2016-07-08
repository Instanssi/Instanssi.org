# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http.response import JsonResponse
from django.http import Http404
from Instanssi.kompomaatti.models import Event, Compo, Entry, Competition, CompetitionParticipation
from Instanssi.kompomaatti.misc import entrysort
from Instanssi.arkisto.models import OtherVideoCategory, OtherVideo
from common.misc import get_url


def text_event(request, event_id):
    _event = get_object_or_404(Event, pk=int(event_id), archived=True)

    # Get all compos that are active but not hidden from archive
    compos = []
    for compo in Compo.objects.filter(event=_event, active=True, hide_from_archive=False):
        if compo.show_voting_results:
            compo.entries = entrysort.sort_by_score(Entry.objects.filter(compo=compo))
        else:
            compo.entries = Entry.objects.filter(compo=compo).order_by('name')
        compos.append(compo)

    # Render Event frontpage
    return render_to_response('arkisto/results.txt', {
        'event': _event,
        'compos': compos,
    }, context_instance=RequestContext(request), content_type='text/plain; charset=utf-8')


def json_event(request, event_id):
    _event = get_object_or_404(Event, pk=int(event_id), archived=True)

    # Get all compos that are active but not hidden from archive
    entries_out = []
    compos_out = []
    for c in Compo.objects.filter(event=_event, active=True, hide_from_archive=False):
        if c.show_voting_results:
            entries = entrysort.sort_by_score(Entry.objects.filter(compo=c))
        else:
            entries = Entry.objects.filter(compo=c).order_by('name')

        compos_out.append({
            'id': c.pk,
            'name': c.name,
            'entry_count': len(entries)
        })

        for e in entries:
            entries_out.append({
                'id': e.id,
                'compo_name': c.name,
                'compo_id': c.pk,
                'entry_name': e.name,
                'entry_author': e.creator,
                'entry_score': round(e.get_score(), 2),
                'entry_rank': e.get_rank(),
                'entry_result_url': get_url(e.entryfile.url),
                'entry_source_url': get_url(e.sourcefile.url) if e.sourcefile else None,
                'entry_youtube_url': get_url(e.youtube_url) if e.youtube_url else None,
                'entry_image_thumbnail': get_url(e.imagefile_thumbnail.url) if e.imagefile_thumbnail else None,
                'entry_image_medium': get_url(e.imagefile_medium.url) if e.imagefile_medium else None,
                'entry_image_original': get_url(e.imagefile_original.url) if e.imagefile_original else None
            })

    return JsonResponse({
        'entries': entries_out,
        'compos': compos_out
    })


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
        
    # Get competitions
    competitionlist = []
    comps = Competition.objects.filter(event=event, active=True, hide_from_archive=False).order_by('name')
    for comp in comps:
        rankby = '-score'
        if comp.score_sort == 1:
            rankby = 'score'
        comp.participants = CompetitionParticipation.objects.filter(competition=comp).order_by(rankby)
        competitionlist.append(comp)
    
    # Render Event frontpage
    return render_to_response('arkisto/index.html', {
        'event': event,
        'compos': compolist,
        'videos': videolist,
        'competitionlist': competitionlist,
    }, context_instance=RequestContext(request))


# Index page (loads event page)
def index(request):
    try:
        latest = Event.objects.filter(archived=True).latest('date')
    except Event.DoesNotExist:
        return render_to_response('arkisto/empty.html', context_instance=RequestContext(request))
            
    return event(request, latest.id)


# Entry page
def entry(request, entry_id):
    # Get the entry
    _entry = get_object_or_404(Entry, pk=entry_id)

    # Make sure the entry belongs to an archived event
    if not _entry.compo.event.archived:
        raise Http404
    
    # Make sure the compo is active and can be shown
    if _entry.compo.hide_from_archive or not _entry.compo.active:
        raise Http404
    
    # Dump the page
    return render_to_response('arkisto/entry.html', {
        'entry': _entry,
        'event': _entry.compo.event,
    }, context_instance=RequestContext(request))


# Video page
def video(request, video_id):
    # Get the entry
    _video = get_object_or_404(OtherVideo, pk=video_id)

    # Make sure the entry belongs to an archived event
    if not _video.category.event.archived:
        raise Http404
    
    # Dump the page
    return render_to_response('arkisto/video.html', {
        'video': _video,
        'event': _video.category.event,
    }, context_instance=RequestContext(request))
