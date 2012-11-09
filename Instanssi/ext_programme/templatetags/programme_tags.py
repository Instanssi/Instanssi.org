# -*- coding: utf-8 -*-

from django import template
from Instanssi.kompomaatti.models import Event

register = template.Library()

@register.inclusion_tag('ext_programme/tags/programme.html')
def render_programme(event_id):
    return {
        'event_id': event_id,
    }
