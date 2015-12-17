# -*- coding: utf-8 -*-

from common.rest import rest_api, RestResponse
from Instanssi.kompomaatti.models import Event
from common.responses import JSONResponse
from Instanssi.kompomaatti.misc.events import get_upcoming


@rest_api
def events_get(request):
    return RestResponse()


@rest_api
def compos_get(request):
    return RestResponse()


@rest_api
def competitions_get(request):
    return RestResponse()


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

    return JSONResponse({'events': events})
