# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from Instanssi.kompomaatti.models import Compo, VoteCode
from django.template import RequestContext
from Instanssi.settings import ACTIVE_EVENT_ID

def custom_render(request, tpl, context={}):
    context['compos'] = Compo.objects.filter(active=True, event=ACTIVE_EVENT_ID)
    context['logged'] = request.user.is_authenticated()
    context['is_su'] = request.user.is_superuser
    associated = False
    votecode = None
    try:
        votecode = VoteCode.objects.get(associated_to=request.user)
        associated = True
    except:
        pass
    context['associated'] = associated
    context['votecode'] = votecode
    return render_to_response(tpl, context, context_instance=RequestContext(request))