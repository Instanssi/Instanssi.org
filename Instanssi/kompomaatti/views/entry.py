# -*- coding: utf-8 -*-

from django.http import Http404

from Instanssi.kompomaatti.misc.custom_render import custom_render
from Instanssi.kompomaatti.models import Entry

def entry(request, entry_id):
    # Get the entry. Show 404 if it doesn't exist ...
    try:
        entry = Entry.objects.get(id=entry_id)
    except ObjectDoesNotExist:
        raise Http404
    
    # Init dict that tells what we should show in the entry view
    show = {
        'youtube': False,
        'image': False,
        'jplayer': False,
    }
    
    # Select which views can be shown
    state = entry.compo.entry_view_type
    if state == 1:
        if entry.youtube_url:
            show['youtube'] = True
        elif entry.imagefile_original:
            show['image'] = True
    elif state == 2:
        if entry.imagefile_original:
            show['image'] = True
    elif state == 3:
        if entry.can_use_jplayer():
            show['jplayer'] = True
        elif entry.imagefile_original:
            show['image'] = True
    
    # Render the template
    return custom_render(request, 'kompomaatti/entry.html', {
        'entry': entry,
        'show': show,
    })