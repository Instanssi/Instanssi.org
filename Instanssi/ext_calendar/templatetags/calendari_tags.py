# -*- coding: utf-8 -*-

from django import template
from Instanssi.kompomaatti.models import Event

register = template.Library()

@register.inclusion_tag('ext_calendar/tags/calendar.html')
def render_calendar(event_id):
    return {
        'event_id': event_id,
    }
