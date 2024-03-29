import time

import arrow
from django import template
from django.conf import settings
from django.urls import reverse

from Instanssi.ext_programme.models import ProgrammeEvent
from Instanssi.kompomaatti.models import Competition, Compo

register = template.Library()


@register.inclusion_tag("ext_programme/tags/programme.html")
def render_programme(event_id):
    progs = ProgrammeEvent.objects.filter(event_id=event_id, event_type=1, active=True).order_by("start")

    return {
        "event_id": event_id,
        "progs": progs,
    }


@register.inclusion_tag("ext_programme/tags/calendar.html")
def render_calendar(event_id):
    compos = Compo.objects.filter(event_id=event_id, active=True)
    progs = ProgrammeEvent.objects.filter(event_id=event_id, active=True)
    comps = Competition.objects.filter(event_id=event_id, active=True)

    # Results go here
    events = []

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
    def helper(obj):
        return time.mktime(obj["date"].timetuple())

    events = sorted(events, key=helper)

    # Group by day
    grouped_events = {}
    keys = []
    for event in events:
        d = event["date"].date()
        if d not in grouped_events:
            grouped_events[d] = []
            keys.append(d)
        grouped_events[d].append(event)

    # Final list for template
    events = []
    for key in keys:
        days = [
            "Maanantai",
            "Tiistai",
            "Keskiviikko",
            "Torstai",
            "Perjantai",
            "Lauantai",
            "Sunnuntai",
        ]
        dt = arrow.get(key).to(settings.TIME_ZONE).format("DD.MM.")
        events.append(
            {
                "items": grouped_events[key],
                "title": "{} {}".format(days[key.weekday()], dt),
            }
        )

    # All done
    return {
        "event_id": event_id,
        "events": events,
    }
