# -*- coding: utf-8 -*-

from django import template
from Instanssi.kompomaatti.models import Event

register = template.Library()

@register.inclusion_tag('admin_base/event_nav_items.html')
def render_base_events_nav():
    return {'events': Event.objects.all().order_by('-date')}

@register.simple_tag
def event_name(event_id):
    try:
        event = Event.objects.get(pk=event_id)
        return event.name
    except:
        pass
    return ''