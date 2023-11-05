from typing import Any, Dict, List

from django.http import HttpRequest, HttpResponse

from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.common.auth import staff_access_required
from Instanssi.kompomaatti.models import Compo, Entry, Event, VoteCodeRequest


@staff_access_required
def index(request: HttpRequest) -> HttpResponse:
    # Flag that tells if there are any important notices for the user
    important_flag = False

    # Check if there are any waiting votecode requests
    vote_code_requests: List[Dict[str, Any]] = []
    events = Event.objects.all()
    for event in events:
        rcount = VoteCodeRequest.objects.filter(event=event, status=0).count()
        if rcount > 0:
            important_flag = True
            vote_code_requests.append(
                {
                    "count": rcount,
                    "event_id": event.id,
                    "event_name": event.name,
                }
            )

    # Find total disk usage for entries
    entries = Entry.objects.all()
    disk_usage: int = 0
    for entry in entries:
        try:
            disk_usage += entry.entryfile.size if entry.entryfile else 0
            disk_usage += entry.sourcefile.size if entry.sourcefile else 0
            disk_usage += entry.imagefile_original.size if entry.imagefile_original else 0
        except OSError:
            pass

    # Get some statistics
    stats = {
        "events": Event.objects.all().count(),
        "entries": Entry.objects.all().count(),
        "compos": Compo.objects.all().count(),
        "space_usage": disk_usage,
    }

    return admin_render(
        request,
        "admin_base/index.html",
        {
            "real_name": request.user.get_full_name(),
            "important_flag": important_flag,
            "vcreqs": vote_code_requests,
            "stats": stats,
        },
    )
