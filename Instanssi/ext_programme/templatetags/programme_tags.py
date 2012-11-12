# -*- coding: utf-8 -*-

from django import template
from Instanssi.kompomaatti.models import Event,Compo,Competition
from Instanssi.ext_programme.models import ProgrammeEvent
from django.core.urlresolvers import reverse
import time

register = template.Library()

@register.inclusion_tag('ext_programme/tags/programme.html')
def render_programme(event_id):
    return {
        'event_id': event_id,
    }


@register.inclusion_tag('ext_programme/tags/calendar.html')
def render_calendar(event_id):
    compos = Compo.objects.filter(event_id=event_id)
    progs = ProgrammeEvent.objects.filter(event_id=event_id)
    comps = Competition.objects.filter(event_id=event_id)
    
    # Results go here
    events = []
    
    # Handle compos
    for compo in compos:
        events.append({
            'date': compo.adding_end,
            'title': compo.name+': Deadline.',
            'url': reverse('km:compo', args=(event_id, compo.id,)),
        })
        events.append({
            'date': compo.compo_start,
            'title': compo.name+': kompo alkaa.',
            'url': reverse('km:compo', args=(event_id, compo.id,)),
        })
        events.append({
            'date': compo.voting_start,
            'title': compo.name+': äänestys alkaa.',
            'url': reverse('km:compo', args=(event_id, compo.id,)),
        })
    
    # Handle competitions
    for comp in comps:
        events.append({
            'date': comp.participation_end,
            'title': comp.name+': Deadline.',
            'url': reverse('km:competition', args=(event_id, comp.id,)),
        })
        events.append({
            'date': comp.start,
            'title': comp.name+': kilpailu alkaa.',
            'url': reverse('km:competition', args=(event_id, comp.id,)),
        })
        
    # Handle programmeevents
    for prog in progs:
        events.append({
            'date': prog.start,
            'title': prog.title,
            'url': None,
        })

    # Sort list 
    def helper(object):
        return time.mktime(object['date'].timetuple())
    events = sorted(events, key=helper)
    
    # TODO: Group by day
    # TODO: Combine similar stuff that happens at the same time

    return {
        'event_id': event_id,
        'events': events,
    }
