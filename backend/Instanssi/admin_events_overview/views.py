from django.http import HttpRequest, HttpResponse

from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.common.auth import staff_access_required


@staff_access_required
def index(request: HttpRequest, selected_event_id) -> HttpResponse:
    return admin_render(
        request, "admin_events_overview/index.html", {"selected_event_id": selected_event_id}
    )
