# -*- coding: utf-8 -*-

from common.http import Http403
from django.contrib.auth.decorators import login_required
from Instanssi.admin_base.misc.custom_render import admin_render
from django.conf import settings

@login_required(login_url=getattr(settings, 'ADMIN_LOGIN_URL'))
def index(request, sel_event_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
    
    # Render response
    return admin_render(request, "admin_events_overview/index.html", {
        'selected_event_id': int(sel_event_id),
    })
