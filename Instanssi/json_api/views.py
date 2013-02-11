# -*- coding: utf-8 -*-

from datetime import datetime
import json
from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404

from common.responses import JSONResponse
from common.http import Http403
from Instanssi.kompomaatti.models import Event
from Instanssi.kompomaatti.misc.events import get_upcoming
from Instanssi.screenshow.models import NPSong

def type_ok(request):
    type = request.META.get('CONTENT_TYPE')
    return (type == 'application/json')

def happenings_api(request):
    happenings = []
    for h in Event.objects.all().order_by("-date"):
        happenings.append({
            'id': h.id,
            'name': h.name,
            'date': h.date.strftime("%d.%m.%Y %H:%M"),
        })
    return JSONResponse({'happenings': happenings})

def events_api(request, hid):
    # Get event
    e = None
    try:
        e = Event.objects.get(pk=hid)
    except Event.DoesNotExist:
        return JSONResponse({'error': 1});

    # Get upcoming stuff
    events = []
    for event in get_upcoming(e):
        event['date'] = event['date'].strftime("%d.%m.%Y %H:%M")
        events.append(event)

    return JSONResponse({'events': events});

def screen_np_get(request):
    if not type_ok(request):
        raise Http404

    # Make sure the request is ok
    try:
        data = json.loads(request.raw_post_data)
        event_id = data['event_id']
    except:
        return JSONResponse({'error': 'Invalid JSON request'});

    # Get song
    try:
        song = NPSong.objects.filter(event_id=event_id).latest('time')
    except:
        raise Http404
    
    # Respond with correct state
    if song.state == 1:
        return JSONResponse({
            'state': u'stop',
            'title': u'',
            'artist': u''
        });                     
    else:
        return JSONResponse({
            'state': u'play',
            'title': song.title,
            'artist': song.artist    
        });

def screen_np_set(request):
    if not type_ok(request):
        raise Http404
   
    # Make sure the request is ok
    try:
        data = json.loads(request.raw_post_data)
        key = data['key']
        title = data['title']
        event_id = data['event_id']
        artist = data['artist']
        type = data['type']
    except:
        return JSONResponse({'error': 'Invalid JSON request'});
    
    # Check the key
    if settings.JSON_KEY != key:
        raise Http403
    
    # Get event, make sure it exists.
    event = get_object_or_404(Event, pk=event_id)
    
    # Save as new song
    try:
        song = NPSong()
        song.event = event
        song.title = title
        song.artist = artist
        song.time = datetime.now()
        song.state = 0
        if type == 'stop':
            song.state = 1
        song.save()
    except:
        return JSONResponse({'error': 'Database error'});
    
    # Delete earliest NPSong
    if NPSong.objects.count() >= 10:
        NPSong.objects.earliest('time').delete()
    
    # All done. Just return nothing.
    return JSONResponse({});
