# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from common.responses import JSONResponse
from Instanssi.kompomaatti.models import Event
from Instanssi.kompomaatti.misc.events import get_upcoming

def index(request, event_id):
    return render_to_response('screenshow/index.html', {'event_id': event_id}, context_instance=RequestContext(request))

def api(request, event_id):
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