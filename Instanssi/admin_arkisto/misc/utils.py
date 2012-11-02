# -*- coding: utf-8 -*-

from datetime import datetime, date
from Instanssi.kompomaatti.models import Event, Compo, Competition, Entry

def is_votes_unoptimized(compo_ids):
    entries = Entry.objects.filter(compo__in=compo_ids, archive_score=None)
    if len(entries) > 0:
        return True
        
    entries = Entry.objects.filter(compo__in=compo_ids, archive_rank=None)
    if len(entries) > 0:
        return True
    
    return False


def is_event_ongoing(event):
    if event.date > date.today():
        return True
    
    compos = Compo.objects.filter(event=event, voting_end__gt=datetime.now())
    if len(compos) > 0:
        return True
    
    compos = Compo.objects.filter(event=event, compo_start__gt=datetime.now())
    if len(compos) > 0:
        return True

    compos = Compo.objects.filter(event=event, adding_end__gt=datetime.now())
    if len(compos) > 0:
        return True

    competitions = Competition.objects.filter(event=event, end__gt=datetime.now())
    if len(competitions) > 0:
        return True

    competitions = Competition.objects.filter(event=event, start__gt=datetime.now())
    if len(competitions) > 0:
        return True
            
    return False