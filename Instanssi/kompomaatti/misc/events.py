import time
from typing import Any, Dict, List

from django.utils import timezone

from Instanssi.ext_programme.models import ProgrammeEvent
from Instanssi.kompomaatti.models import Competition, Compo, Event


def get_upcoming(event: Event) -> List[Dict[str, Any]]:
    compos = Compo.objects.filter(event=event, voting_end__gt=timezone.now(), active=True)
    progs = ProgrammeEvent.objects.filter(event=event, start__gt=timezone.now(), active=True)
    comps = Competition.objects.filter(event=event, start__gt=timezone.now(), active=True)
    events = []

    # Handle compos
    for compo in compos:
        # Only show this if still valid
        if compo.adding_end > timezone.now():
            events.append(
                {
                    "id": compo.id,
                    "date": compo.adding_end,
                    "title": f"{compo.name}: ilmoittautuminen päättyy.",
                    "type": 1,
                    "icon": "",
                }
            )

        if compo.compo_start > timezone.now():
            events.append(
                {
                    "id": compo.id,
                    "date": compo.compo_start,
                    "title": f"{compo.name}: kompo alkaa.",
                    "type": 1,
                    "icon": "",
                }
            )

        if compo.is_votable:
            events.append(
                {
                    "id": compo.id,
                    "date": compo.voting_end,
                    "title": f"{compo.name}: äänestys päättyy.",
                    "type": 1,
                    "icon": "",
                }
            )

    # Handle competitions
    for comp in comps:
        if comp.participation_end > timezone.now():
            events.append(
                {
                    "id": comp.id,
                    "date": comp.participation_end,
                    "title": f"{comp.name}: ilmoittautuminen päättyy.",
                    "type": 2,
                    "icon": "",
                }
            )
        events.append(
            {
                "id": comp.id,
                "date": comp.start,
                "title": f"{comp.name}: kilpailu alkaa.",
                "type": 2,
                "icon": "",
            }
        )

    # Handle programme events
    for prog in progs:
        icon = None
        if prog.icon_small:
            icon = prog.icon_small.url
        events.append(
            {
                "id": prog.id,
                "date": prog.start,
                "title": prog.title,
                "icon": icon,
                "type": 3,
                "ev_type": prog.event_type,
            }
        )

    # Sort list by datetime
    return sorted(events, key=lambda o: time.mktime(o["date"].timetuple()))
