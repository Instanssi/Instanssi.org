import datetime
import time
from typing import Any

from django import template
from django.urls import reverse
from django.utils.formats import date_format
from django.utils.translation import override as translation_override

from Instanssi.ext_programme.models import ProgrammeEvent
from Instanssi.kompomaatti.models import Competition, Compo

register = template.Library()


@register.inclusion_tag("ext_programme/tags/programme.html")
def render_programme(event_id: int) -> dict[str, Any]:
    progs = ProgrammeEvent.objects.filter(event_id=event_id, event_type=1, active=True).order_by("start")

    return {
        "event_id": event_id,
        "progs": progs,
    }


@register.inclusion_tag("ext_programme/tags/calendar.html")
@translation_override("fi")
def render_calendar(event_id: int) -> dict[str, Any]:
    compos = Compo.objects.filter(event_id=event_id, active=True)
    progs = ProgrammeEvent.objects.filter(event_id=event_id, active=True)
    comps = Competition.objects.filter(event_id=event_id, active=True)

    # Results go here
    events: list[dict[str, Any]] = []

    # Handle compos
    for compo in compos:
        events.append(
            {
                "date": compo.adding_end,
                "title": f"{compo.name}: ilmoittautuminen päättyy",
                "url": reverse("km:compo", args=(event_id, compo.id)),
                "icon": "",
                "place": "",
                "desc": "",
            }
        )
        events.append(
            {
                "date": compo.compo_start,
                "title": f"{compo.name}: kompo alkaa",
                "url": reverse("km:compo", args=(event_id, compo.id)),
                "icon": "",
                "place": "",
                "desc": "",
            }
        )
        if compo.is_votable:
            events.append(
                {
                    "date": compo.voting_end,
                    "title": f"{compo.name}: äänestys päättyy",
                    "url": reverse("km:compo", args=(event_id, compo.id)),
                    "icon": "",
                    "place": "",
                    "desc": "",
                }
            )

    # Handle competitions
    for comp in comps:
        events.append(
            {
                "date": comp.participation_end,
                "title": f"{comp.name}: ilmoittautuminen päättyy",
                "url": reverse("km:competition", args=(event_id, comp.id)),
                "icon": "",
                "place": "",
                "desc": "",
            }
        )
        events.append(
            {
                "date": comp.start,
                "title": f"{comp.name}: kilpailu alkaa",
                "url": reverse("km:competition", args=(event_id, comp.id)),
                "icon": "",
                "place": "",
                "desc": "",
            }
        )

    # Handle programme-events
    for prog in progs:
        icon = None
        if prog.icon_small:
            icon = prog.icon_small.url
        if prog.event_type == 0:
            events.append(
                {
                    "date": prog.start,
                    "title": prog.title,
                    "icon": icon,
                    "url": None,
                    "place": prog.place,
                    "desc": "",
                    "id": f"sp-{prog.id}",
                }
            )
        else:
            events.append(
                {
                    "date": prog.start,
                    "title": prog.presenters,
                    "icon": icon,
                    "url": f"../ohjelma/#{prog.id}",
                    "place": prog.place,
                    "desc": prog.title,
                    "id": f"sp-{prog.id}",
                }
            )

    # Sort list
    def helper(obj: dict[str, Any]) -> float:
        return time.mktime(obj["date"].timetuple())

    events = sorted(events, key=helper)

    # Group by day
    grouped_events: dict[datetime.date, list[dict[str, Any]]] = {}
    keys: list[datetime.date] = []
    for event in events:
        d: datetime.date = event["date"].date()
        if d not in grouped_events:
            grouped_events[d] = []
            keys.append(d)
        grouped_events[d].append(event)

    # Final list for template
    events = []
    for key in keys:
        events.append(
            {
                "items": grouped_events[key],
                "title": date_format(key, "l d.m."),
            }
        )

    # All done
    return {
        "event_id": event_id,
        "events": events,
    }
