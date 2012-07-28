# -*- coding: utf-8 -*-

from Instanssi.kompomaatti.models import Event

def get_selected_event(request):
    if 'm_event_id' not in request.session:
        try:
            event = Event.object.latest('date')[0]
            request.session['m_event_id'] = event.id
        except:
            request.session['m_event_id'] = -1
        
    return request.session['m_event_id']
