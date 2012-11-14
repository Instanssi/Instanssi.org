# -*- coding: utf-8 -*-

from django.http import Http404,HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.admin_base.misc.auth_decorator import staff_access_required

@staff_access_required
def index(request, sel_event_id):
    return admin_render(request, "admin_screenshow/index.html", {
        'selected_event_id': int(sel_event_id),
    })
