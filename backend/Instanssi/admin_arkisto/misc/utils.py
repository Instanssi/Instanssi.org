from typing import TYPE_CHECKING

from django.db.models import QuerySet
from django.utils import timezone

from Instanssi.kompomaatti.models import Competition, Compo, Entry

if TYPE_CHECKING:
    from Instanssi.kompomaatti.models import Event


def is_votes_unoptimized(compo_ids: QuerySet[Compo]) -> bool:
    entries = Entry.objects.filter(compo__in=compo_ids, archive_score=None)
    if len(entries) > 0:
        return True

    entries = Entry.objects.filter(compo__in=compo_ids, archive_rank=None)
    if len(entries) > 0:
        return True

    return False


def is_event_ongoing(event: "Event") -> bool:
    if event.date > timezone.now().date():
        return True

    compos = Compo.objects.filter(event=event, voting_end__gt=timezone.now())
    if len(compos) > 0:
        return True

    compos = Compo.objects.filter(event=event, compo_start__gt=timezone.now())
    if len(compos) > 0:
        return True

    compos = Compo.objects.filter(event=event, adding_end__gt=timezone.now())
    if len(compos) > 0:
        return True

    competitions = Competition.objects.filter(event=event, end__gt=timezone.now())
    if len(competitions) > 0:
        return True

    competitions = Competition.objects.filter(event=event, start__gt=timezone.now())
    if len(competitions) > 0:
        return True

    return False
