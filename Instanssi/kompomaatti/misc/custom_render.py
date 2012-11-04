# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from Instanssi.kompomaatti.models import Event

def custom_render(request, tpl, context={}):
    context['user'] = request.user
    
    # Get event name
    if 'sel_event_id' in context:
        event = get_object_or_404(Event, pk=context['sel_event_id'])
        context['sel_event_name'] = event.name
    
    return render_to_response(tpl, context, context_instance=RequestContext(request))