# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from Instanssi.kompomaatti.models import Event
from django.template import RequestContext

def admin_render(request, tpl, context={}):
    # Events
    context['navmenu_events'] = Event.objects.all()

    # For redirects
    context['full_path'] = request.get_full_path()

    # Render
    return render_to_response(tpl, context, context_instance=RequestContext(request))