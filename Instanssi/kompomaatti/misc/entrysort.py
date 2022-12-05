from typing import TYPE_CHECKING, Iterable, List

if TYPE_CHECKING:
    from Instanssi.kompomaatti.models import Entry


def sort_by_score(entries: Iterable["Entry"], reverse: bool = True) -> List["Entry"]:
    return list(sorted(entries, key=lambda o: o.get_score(), reverse=reverse))
