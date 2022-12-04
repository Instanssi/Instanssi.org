import arrow

from django.shortcuts import render, get_object_or_404
from Instanssi.common.responses import JSONResponse
from Instanssi.kompomaatti.misc.events import get_upcoming
from Instanssi.screenshow.models import *
from django.utils import timezone
from django.conf import settings
from django.utils.safestring import mark_safe


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
        x += 75
        
    # Render the show
    return render(request, 'screenshow/index.html', {
        'event_id': event_id,
        'sponsors': sponsors,
    })


def settings_api(request, event_id):
    # Attempt to fetch custom settings from database
    try:
        conf = {}
        s = ScreenConfig.objects.get(event_id=event_id)
        conf['enable_twitter'] = s.enable_twitter
        conf['enable_irc'] = s.enable_irc
        conf['enable_videos'] = s.enable_videos
        conf['video_interval'] = s.video_interval
        return JSONResponse({'settings': conf})
    except ScreenConfig.DoesNotExist:
        pass
    
    # Return settings
    return JSONResponse({})


def events_api(request, event_id):
    e = get_object_or_404(Event, pk=event_id)

    # Get upcoming stuff
    k = 0
    events = []
    for event in get_upcoming(e):
        event['date'] = arrow.get(event['date']).to(settings.TIME_ZONE).format("HH:mm")
        events.append(event)
        
        # Only pick 5
        k += 1
        if k >= 5:
            break

    return JSONResponse({'events': events})


def playing_api(request, event_id):
    playlist = []
    for item in NPSong.objects.filter(event_id=event_id).order_by('-id')[:10]:
        playlist.append({
            'title': item.title,
            'artist': item.artist,
            'state': item.state,
        })
    return JSONResponse({'playlist': playlist})


def messages_api(request, event_id):
    messages = []
    for msg in Message.objects.filter(event_id=event_id):
        if msg.show_start <= timezone.now() <= msg.show_end:
            messages.append(mark_safe(msg.text))
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
            'time': arrow.get(msg.date).to(settings.TIME_ZONE).format("HH:mm")
        })
        
    # Respond
    return JSONResponse({'log': messages})
