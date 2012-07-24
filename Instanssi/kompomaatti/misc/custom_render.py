# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from Instanssi.kompomaatti.models import Compo, VoteCode
from django.template import RequestContext
from Instanssi.dbsettings.models import Setting

def custom_render(request, tpl, context={}):
    active_event_id = Setting.get('active_event_id', 'events', -1)
    context['compos'] = Compo.objects.filter(active=True, event=active_event_id)
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