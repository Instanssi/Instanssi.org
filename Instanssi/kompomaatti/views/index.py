# -*- coding: utf-8 -*-

from Instanssi.kompomaatti.misc.custom_render import custom_render
from Instanssi.kompomaatti.models import Compo
from datetime import datetime
from Instanssi.dbsettings.models import Setting

def index(request):
    # Get active event id
    active_event_id = Setting.get('active_event_id', 'events', -1)
    
    # Get events
    events = Compo.objects.filter(compo_start__gt=datetime.now(), event=active_event_id, active=True).order_by('compo_start')
    
    # Render frontpage
    return custom_render(request, 'kompomaatti/index.html', {
        'events': events
    })