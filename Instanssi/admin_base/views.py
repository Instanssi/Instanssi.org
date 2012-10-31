# -*- coding: utf-8 -*-

from common.http import Http403
from django.contrib.auth.decorators import login_required
from Instanssi.admin_base.misc.custom_render import admin_render

@login_required(login_url='/manage/auth/login/')
def index(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
    
    # Render response
    return admin_render(request, "admin_base/index.html", {})
