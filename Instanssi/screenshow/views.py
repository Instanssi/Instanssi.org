# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from common.responses import JSONResponse
from Instanssi.kompomaatti.models import Event
from Instanssi.kompomaatti.misc.events import get_upcoming
from Instanssi.screenshow.models import *
from datetime import datetime

def index(request, event_id):
    # Get sponsors
    sponsors = []
    x = -300
    for sponsor in Sponsor.objects.filter(event_id=event_id):
        sponsor.x = x
        sponsor.z = 500
        sponsor.y = -270
        sponsor.rot_x = 0
        sponsor.rot_y = 30
        sponsor.rot_z = 90
        sponsors.append(sponsor)
        x += 100
        
    # Render the show
    return render_to_response('screenshow/index.html', {
        'event_id': event_id,
        'sponsors': sponsors,
    }, context_instance=RequestContext(request))

def events_api(request, event_id):
    e = get_object_or_404(Event, pk=event_id)

    # Get upcoming stuff
    k = 0
    events = []
    for event in get_upcoming(e):
        event['date'] = event['date'].strftime("%H:%M")
        events.append(event)
        
        # Only pick 5
        k = k + 1
        if k >= 5:
            break;

    return JSONResponse({'events': events});

def messages_api(request, event_id):
    messages = []
    for msg in Message.objects.filter(event_id=event_id):
        if msg.show_start <= datetime.now() and msg.show_end >= datetime.now():
            messages.append(msg.text)
    return JSONResponse({'messages': messages})

def playlist_api(request, event_id):
    playlist = []
    for v in PlaylistVideo.objects.filter(event_id=event_id).order_by('index'):
        playlist.append({
            'name': v.name,
            'url': v.url,
            'id': v.id,
            'index': v.index
        })
    
    return JSONResponse({'playlist': playlist})

def irc_api(request, event_id):
    # See if we got request data
    filter_id = 0
    try:
        filter_id = request.GET['last_id']
    except:
        pass
        
    # handle datetimes
    messages = []
    for msg in IRCMessage.objects.filter(id__gt=filter_id, event_id=event_id):
        messages.append({
            'id': msg.id,
            'text': msg.message,
            'nick': msg.nick,
            'time': msg.date.strftime("%H:%M"),
        })
        
    # Respond
    return JSONResponse({'log': messages})
