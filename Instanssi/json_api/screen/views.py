# -*- coding: utf-8 -*-

from datetime import datetime
import json
from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from common.responses import JSONResponse
from common.http import Http403
from Instanssi.kompomaatti.models import Event
from Instanssi.screenshow.models import NPSong


@csrf_exempt
def song_get(request):
    # Make sure the request is ok
    try:
        data = json.loads(request.body)
        event_id = data['event_id']
    except:
        return JSONResponse({'error': 'Invalid JSON request'})

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
        })
    else:
        return JSONResponse({
            'state': u'play',
            'title': song.title,
            'artist': song.artist    
        })


@csrf_exempt
def song_set(request):
    # Make sure the request is ok
    try:
        data = json.loads(request.body)
        key = data['key']
        event_id = data['event_id']
        type = data['type']
    except:
        return JSONResponse({'error': 'Invalid JSON request'})
    
    # Get artist and title, if they exist
    try:
        artist = data['artist']
        title = data['title']
    except:
        artist = u''
        title = u''
    
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
        return JSONResponse({'error': 'Database error'})
    
    # Delete earliest NPSong
    scount = NPSong.objects.count()
    if scount > 10:
        k = scount - 10
        for song in NPSong.objects.order_by('id'):
            if k <= 0:
                break
            k -= 1
            song.delete()
    
    # All done. Just return nothing.
    return JSONResponse({})
