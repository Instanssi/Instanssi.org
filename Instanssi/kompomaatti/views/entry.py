# -*- coding: utf-8 -*-

from django.http import Http404

from Instanssi.kompomaatti.misc.custom_render import custom_render
from Instanssi.kompomaatti.models import Entry, Compo
from Instanssi.dbsettings.models import Setting

def entry(request, entry_id):
    # Get active event id
    active_event_id = Setting.get('active_event_id', 'events', -1)
    
    # Get the entry. Show 404 if it doesn't exist ...
    try:
        entry = Entry.objects.get(id=entry_id, compo__in=Compo.objects.filter(event=active_event_id))
    except Entry.DoesNotExist:
        raise Http404
            
    # Render the template
    return custom_render(request, 'kompomaatti/entry.html', {
        'entry': entry,
        'show': entry.get_show_list(),
    })