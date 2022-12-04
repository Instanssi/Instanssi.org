from django import template
from Instanssi.kompomaatti.models import Compo, Competition, Event

register = template.Library()


@register.inclusion_tag('kompomaatti/tags/compo_nav_items.html')
def render_base_compos_nav(event_id):
    return {
        'event_id': event_id,
        'compos': Compo.objects.filter(active=True, event_id=event_id)
    }


@register.inclusion_tag('kompomaatti/tags/competition_nav_items.html')
def render_base_competitions_nav(event_id):
    return {
        'event_id': event_id,
        'competitions': Competition.objects.filter(active=True, event_id=event_id)
    }


@register.inclusion_tag('kompomaatti/tags/count.html')
def render_base_compos_count(event_id):
    return {'count': Compo.objects.filter(active=True, event_id=event_id).count()}


@register.inclusion_tag('kompomaatti/tags/count.html')
def render_base_competitions_count(event_id):
    return {'count': Competition.objects.filter(active=True, event_id=event_id).count()}


@register.simple_tag
def event_name(event_id):
    try:
        event = Event.objects.get(pk=event_id)
        return event.name
    except Event.DoesNotExist:
        pass
    return ''
