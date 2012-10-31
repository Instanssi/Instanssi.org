# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from Instanssi.kompomaatti.models import Event
from django.template import RequestContext

def admin_render(request, tpl, context={}):
    context['navmenu_events'] = Event.objects.all()
    context['full_path'] = request.get_full_path()
    
    # H4x
    if 'selected_event_id' in context:
        event = Event.objects.get(pk=context['selected_event_id'])
        context['selected_event_name'] = event.name 

    # Render
    return render_to_response(tpl, context, context_instance=RequestContext(request))