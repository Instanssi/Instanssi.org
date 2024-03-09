from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from django.urls import reverse
from django_ical.views import ICalFeed

from Instanssi.ext_programme.models import ProgrammeEvent
from Instanssi.kompomaatti.models import Competition, Compo


@dataclass
class Event:
    start_time: datetime
    title: str
    description: str
    url: str


class EventFeed(ICalFeed):
    """
    A simple event calender
    """

    product_id = "-//instanssi.org//Events//EN"
    timezone = "UTC"
    file_name = "instanssi.ics"

    def items(self):
        events: list[Event] = []
        start = datetime.now(timezone.utc) - timedelta(days=365)
        for compo in Compo.objects.filter(compo_start__gt=start):
            compo_url = reverse("km:compo", args=(compo.event_id, compo.id))
            events.append(
                Event(
                    start_time=compo.adding_end,
                    title=f"Compo '{compo.name}' deadline",
                    description=f"Compo '{compo.name}' deadline for new entries",
                    url=compo_url,
                )
            )
            events.append(
                Event(
                    start_time=compo.compo_start,
                    title=f"Compo '{compo.name}' begins",
                    description=f"Compo '{compo.name}' begins",
                    url=compo_url,
                )
            )
            events.append(
                Event(
                    start_time=compo.voting_end,
                    title=f"Compo '{compo.name}' voting ends",
                    description=f"Compo '{compo.name}' voting deadline",
                    url=compo_url,
                )
            )
        for competition in Competition.objects.filter(start__gt=start):
            competition_url = reverse("km:competition", args=(competition.event_id, competition.id))
            events.append(
                Event(
                    start_time=competition.participation_end,
                    title=f"Competition '{competition.name}' signup deadline",
                    description=f"Competition '{competition.name}' deadline for competition signups",
                    url=competition_url,
                )
            )
            events.append(
                Event(
                    start_time=competition.start,
                    title=f"Competition '{competition.name}' begins",
                    description=f"Competition '{competition.name}' begins",
                    url=competition_url,
                )
            )
        for program in ProgrammeEvent.objects.filter(start__gt=start):
            events.append(
                Event(
                    start_time=program.start,
                    title=f"Event '{program.title}' begins",
                    description=f"Event '{program.title}' begins",
                    url=reverse("km"),
                )
            )
        return events

    def item_title(self, item: Event) -> str:
        return item.title

    def item_description(self, item: Event) -> str:
        return item.description

    def item_start_datetime(self, item: Event) -> datetime:
        return item.start_time

    def item_link(self, item: Event) -> str:
        return item.url
