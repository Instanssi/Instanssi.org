# -*- coding: utf-8 -*-

from datetime import datetime
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from Instanssi.common.rest import RestResponse, rest_api
from Instanssi.common.http import Http403
from Instanssi.kompomaatti.models import Event
from Instanssi.screenshow.models import NPSong


@csrf_exempt
@rest_api
def song_get(request):
    # Make sure the request is ok
    try:
        event_id = request.GET['event_id']
    except KeyError:
        return RestResponse(code=400, error_text=u'Invalid request')

    # Get song
    try:
        song = NPSong.objects.filter(event_id=event_id).latest('time')
    except NPSong.DoesNotExist:
        return RestResponse({})
    
    # Respond with correct state
    return RestResponse({
        'state': u'stop' if song.state == 1 else u'play',
        'title': song.title,
        'artist': song.artist
    })


@csrf_exempt
@rest_api
def song_set(request):
    # Make sure the request is ok
    try:
        key = request.json_data['key']
        event_id = request.json_data['event_id']
        state = request.json_data['state']
    except KeyError:
        return RestResponse(code=400, error_text=u'Invalid request')
    
    # Get artist and title, if they exist
    artist = request.json_data.get('artist', u'')
    title = request.json_data.get('title', u'')

    # Check the key
    if settings.JSON_KEY != key:
        raise Http403
    
    # Get event, make sure it exists.
    event = get_object_or_404(Event, pk=event_id)
    
    # Save as new song
    NPSong.objects.create(
        event=event,
        title=title,
        artist=artist,
        time=datetime.now(),
        state=1 if state == 'stop' else 0
    )

    # All done. Just return nothing.
    return RestResponse({})
