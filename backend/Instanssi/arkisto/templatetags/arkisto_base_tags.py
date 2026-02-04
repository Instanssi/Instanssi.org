from typing import Any

from django import template

from Instanssi.kompomaatti.models import Event

register = template.Library()


@register.inclusion_tag("arkisto/arkisto_nav_items.html")
def render_arkisto_nav() -> dict[str, Any]:
    return {"events": Event.objects.filter(archived=True).order_by("-date")}
