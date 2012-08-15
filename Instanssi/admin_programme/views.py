# -*- coding: utf-8 -*-

from django.http import Http404
from django.contrib.auth.decorators import login_required
from Instanssi.admin_base.misc.custom_render import admin_render

@login_required(login_url='/control/auth/login/')
def index(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Render response
    return admin_render(request, "admin_programme/index.html", {})