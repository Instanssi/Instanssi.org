# -*- coding: utf-8 -*-

from django import template
from Instanssi.kompomaatti.models import Compo

register = template.Library()


@register.inclusion_tag('kompomaatti/tags/compo_desc_list.html')
def render_frontpage_compolist(event_id):
    return {
        'event_id': event_id,
        'compos': Compo.objects.filter(event_id=event_id, hide_from_frontpage=False)
    }


@register.inclusion_tag('kompomaatti/tags/compo_desc_content_list.html')
def render_frontpage_compolist_contents(event_id):
    return {
        'event_id': event_id,
        'compos': Compo.objects.filter(event_id=event_id, hide_from_frontpage=False)
    }