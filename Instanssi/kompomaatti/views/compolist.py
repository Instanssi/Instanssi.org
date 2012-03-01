# -*- coding: utf-8 -*-

from operator import itemgetter

from Instanssi.kompomaatti.misc.custom_render import custom_render
from Instanssi.kompomaatti.misc.time_formatting import compo_times_formatter
from Instanssi.kompomaatti.models import Entry, Compo, Vote
from Instanssi.settings import ACTIVE_EVENT_ID

# Helper function for sorting by entry score
def sort_by_score(object):
    return object.get_score()

def compolist(request):
    # Get compos, format times
    composet = Compo.objects.filter(active=True, event=ACTIVE_EVENT_ID).order_by('compo_start')
    compos = []
    for compo in composet:
        compos.append(compo_times_formatter(compo))
    
    # Get entries in compos. If compo has been flagged to show voting results, 
    # then get those. Otherwise just show entries in alphabetical order (by entry name).
    entries = {}
    for compo in compos:
        if compo.show_voting_results:
            # Sort entries by score, highest score first (of course).
            entries[compo.id] = sorted(Entry.objects.filter(compo=compo), key=sort_by_score, reverse=True)
        else:
            # Just get entries in alphabetical order
            entries[compo.id] = Entry.objects.filter(compo=compo).order_by('name')

    # Return page
    return custom_render(request, 'kompomaatti/compolist.html', {
        'compolist': compos,
        'entries': entries
    })