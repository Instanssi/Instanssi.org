# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext
from Instanssi.kompomaatti.models import Event

def admin_render(request, tpl, context={}):
    return render_to_response(tpl, context, context_instance=RequestContext(request))