# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from Instanssi.kompomaatti.models import Event
from django.template import RequestContext
from Instanssi.dbsettings.models import Setting

def admin_render(request, tpl, context={}):
    # Get active event (shown for normal users)
    context['active_event_id'] = Setting.get('active_event_id', 'events', -1)
    
    # Choose the event selected for handling in the admin panel
    if 'm_event_id' in request.session:
        context['selected_event_id'] = request.session['m_event_id']
    else:
        context['selected_event_id'] = context['active_event_id']
    
    # Events
    context['navmenu_events'] = Event.objects.all()
    context['show_eventdep_menus'] = True
    if context['selected_event_id'] == -1:
        context['show_eventdep_menus'] = False
    
    # For redirects
    context['full_path'] = request.get_full_path()

    # Render
    return render_to_response(tpl, context, context_instance=RequestContext(request))