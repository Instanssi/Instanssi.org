from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404

from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.common.auth import staff_access_required
from Instanssi.kompomaatti.misc import entrysort
from Instanssi.kompomaatti.models import Compo, Entry


@staff_access_required
def index(request: HttpRequest, selected_event_id: int) -> HttpResponse:
    return admin_render(
        request,
        "admin_slides/index.html",
        {
            "compos": Compo.objects.filter(event_id=selected_event_id),
            "selected_event_id": selected_event_id,
        },
    )


@staff_access_required
def slide_results(request: HttpRequest, selected_event_id: int, compo_id: int) -> HttpResponse:
    c = get_object_or_404(Compo, pk=compo_id)
    s_entries = entrysort.sort_by_score(Entry.objects.filter(compo=c, disqualified=False))

    i = 0
    f_entries = []
    for entry in reversed(s_entries[:3]):
        f_entries.append(
            {
                "id": entry.id,
                "creator": entry.creator,
                "name": entry.name,
                "platform": entry.platform,
                "score": entry.get_score(),
                "score_x": 0,
                "score_y": i * 2000,
                "score_z": i * 2000,
                "info_x": 0,
                "info_y": i * 2000 + 2000,
                "info_z": i * 2000 + 2000,
                "rank": entry.get_rank(),
            }
        )
        i += 2

    r_entries = []
    for entry in s_entries[3:]:
        r_entries.append(
            {
                "id": entry.id,
                "creator": entry.creator,
                "name": entry.name,
                "score": entry.get_score(),
                "rank": entry.get_rank(),
            }
        )

    i += 1

    return admin_render(
        request,
        "admin_slides/slide_results.html",
        {
            "entries": f_entries,
            "r_entries": r_entries,
            "compo": c,
            "endinfo_x": 0,
            "endinfo_y": (i + 1) * 2000,
            "endinfo_z": (i + 1) * 2000,
            "last_x": 0,
            "last_y": (i + 2) * 2000,
            "last_z": (i + 2) * 2000,
            "selected_event_id": selected_event_id,
        },
    )


@staff_access_required
def slide_entries(request: HttpRequest, selected_event_id: int, compo_id: int) -> HttpResponse:
    c = get_object_or_404(Compo, pk=compo_id)
    s_entries = entrysort.sort_by_score(Entry.objects.filter(compo=c, disqualified=False))

    i = 0
    flip = False
    f_entries = []
    for entry in s_entries:
        if flip:
            g = 180
        else:
            g = 0
        f_entries.append(
            {
                "id": entry.id,
                "creator": entry.creator,
                "name": entry.name,
                "platform": entry.platform,
                "x": 0,
                "y": -i * 2500,
                "z": 0,
                "rot_y": 0,
                "rot_x": g,
                "rot_z": 0,
            }
        )
        i += 1
        flip = not flip

    return admin_render(
        request,
        "admin_slides/slide_entries.html",
        {
            "entries": f_entries,
            "compo": c,
            "last_y": -i * 2500,
            "last_rot_x": flip,
            "selected_event_id": selected_event_id,
        },
    )
