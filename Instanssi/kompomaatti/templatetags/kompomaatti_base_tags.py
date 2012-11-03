# -*- coding: utf-8 -*-

from django import template
from Instanssi.kompomaatti.models import Compo, Competition

register = template.Library()

@register.inclusion_tag('kompomaatti/compo_nav_items.html')
def render_base_compos_nav(event_id):
    return {'compos': Compo.objects.filter(active=True, event_id=event_id)}

@register.inclusion_tag('kompomaatti/competition_nav_items.html')
def render_base_competitions_nav(event_id):
    return {'competitions': Competition.objects.filter(event_id=event_id)}
