from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from django.urls import reverse
from django_ical.views import ICalFeed

from Instanssi.ext_programme.models import ProgrammeEvent
from Instanssi.kompomaatti.models import Competition, Compo


@dataclass
class Event:
    id: str
    start_time: datetime
    title: str
    description: str
    url: str
    end_time: datetime | None = None


class EventFeed(ICalFeed):  # type: ignore[misc]
    title = "Instanssi"
    description = "Instanssi event calendar"
    product_id = "-//instanssi.org//Events//EN"
    timezone = "UTC"
    file_name = "instanssi.ics"

    def items(self) -> list[Event]:
        events: list[Event] = []
        start = datetime.now(timezone.utc) - timedelta(days=365)
        for compo in Compo.objects.filter(compo_start__gt=start, active=True):
            compo_url = reverse("km:compo", args=(compo.event_id, compo.id))
            events.append(
                Event(
                    id=f"compo-{compo.id}-entry-deadline@instanssi.org",
                    start_time=compo.adding_end,
                    title=f"Compo '{compo.name}' deadline",
                    description=f"Compo '{compo.name}' deadline for new entries",
                    url=compo_url,
                )
            )
            events.append(
                Event(
                    id=f"compo-{compo.id}-start@instanssi.org",
                    start_time=compo.compo_start,
                    title=f"Compo '{compo.name}' begins",
                    description=f"Compo '{compo.name}' begins",
                    url=compo_url,
                )
            )
            events.append(
                Event(
                    id=f"compo-{compo.id}-voting-deadline@instanssi.org",
                    start_time=compo.voting_end,
                    title=f"Compo '{compo.name}' voting ends",
                    description=f"Compo '{compo.name}' voting deadline",
                    url=compo_url,
                )
            )
        for competition in Competition.objects.filter(start__gt=start, active=True):
            competition_url = reverse("km:competition", args=(competition.event_id, competition.id))
            events.append(
                Event(
                    id=f"competition-{competition.id}-signup-deadline@instanssi.org",
                    start_time=competition.participation_end,
                    title=f"Competition '{competition.name}' signup deadline",
                    description=f"Competition '{competition.name}' deadline for competition signups",
                    url=competition_url,
                )
            )
            events.append(
                Event(
                    id=f"competition-{competition.id}-start@instanssi.org",
                    start_time=competition.start,
                    end_time=competition.end,
                    title=f"Competition '{competition.name}' begins",
                    description=f"Competition '{competition.name}' begins",
                    url=competition_url,
                )
            )
        for program in ProgrammeEvent.objects.filter(start__gt=start, active=True):
            events.append(
                Event(
                    id=f"event-{program.id}-start@instanssi.org",
                    start_time=program.start,
                    end_time=program.end,
                    title=f"Event '{program.title}' begins",
                    description=f"Event '{program.title}' begins",
                    url=reverse("km:index", args=(program.event_id,)),
                )
            )
        return sorted(events, key=lambda x: x.start_time)

    def item_guid(self, item: Event) -> str:
        return item.id

    def item_title(self, item: Event) -> str:
        return item.title

    def item_description(self, item: Event) -> str:
        return item.description

    def item_start_datetime(self, item: Event) -> datetime:
        return item.start_time

    def item_end_datetime(self, item: Event) -> datetime | None:
        return item.end_time

    def item_link(self, item: Event) -> str:
        return item.url
