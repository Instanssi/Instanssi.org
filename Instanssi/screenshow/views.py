import arrow
from django.conf import settings
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.safestring import mark_safe

from Instanssi.kompomaatti.misc.events import get_upcoming
from Instanssi.kompomaatti.models import Event
from Instanssi.screenshow.models import (
    IRCMessage,
    Message,
    NPSong,
    PlaylistVideo,
    ScreenConfig,
    Sponsor,
)


def index(request: HttpRequest, event_id: int) -> HttpResponse:
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

    return render(request, "screenshow/index.html", {"event_id": event_id, "sponsors": sponsors})


def settings_api(request: HttpRequest, event_id: int) -> HttpResponse:
    # Attempt to fetch custom settings from database
    try:
        conf = {}
        s = ScreenConfig.objects.get(event_id=event_id)
        conf["enable_twitter"] = s.enable_twitter
        conf["enable_irc"] = s.enable_irc
        conf["enable_videos"] = s.enable_videos
        conf["video_interval"] = s.video_interval
        return JsonResponse({"settings": conf})
    except ScreenConfig.DoesNotExist:
        return JsonResponse({})


def events_api(request: HttpRequest, event_id: int) -> HttpResponse:
    e = get_object_or_404(Event, pk=event_id)

    # Get upcoming stuff
    events = []
    for event in get_upcoming(e)[:5]:
        event["date"] = arrow.get(event["date"]).to(settings.TIME_ZONE).format("HH:mm")
        events.append(event)

    return JsonResponse({"events": events})


def playing_api(request: HttpRequest, event_id: int) -> HttpResponse:
    playlist = []
    for item in NPSong.objects.filter(event_id=event_id).order_by("-id")[:10]:
        playlist.append(
            {
                "title": item.title,
                "artist": item.artist,
                "state": item.state,
            }
        )
    return JsonResponse({"playlist": playlist})


def messages_api(request: HttpRequest, event_id: int) -> HttpResponse:
    messages = []
    now = timezone.now()
    for msg in Message.objects.filter(event_id=event_id, show_start__lt=now, show_end__gt=now):
        messages.append(mark_safe(msg.text))
    return JsonResponse({"messages": messages})


def playlist_api(request: HttpRequest, event_id: int) -> HttpResponse:
    playlist = []
    for v in PlaylistVideo.objects.filter(event_id=event_id).order_by("index"):
        playlist.append({"name": v.name, "url": v.url, "id": v.id, "index": v.index})
    return JsonResponse({"playlist": playlist})


def irc_api(request: HttpRequest, event_id: int) -> HttpResponse:
    filter_id = int(request.GET.get("last_id", "0"))
    messages = []
    for msg in IRCMessage.objects.filter(id__gt=filter_id, event_id=event_id):
        messages.append(
            {
                "id": msg.id,
                "text": msg.message,
                "nick": msg.nick,
                "time": arrow.get(msg.date).to(settings.TIME_ZONE).format("HH:mm"),
            }
        )
    return JsonResponse({"log": messages})
