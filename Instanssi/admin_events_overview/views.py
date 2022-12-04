from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.common.auth import staff_access_required


@staff_access_required
def index(request, sel_event_id):
    # Render response
    return admin_render(
        request,
        "admin_events_overview/index.html",
        {
            "selected_event_id": int(sel_event_id),
        },
    )
