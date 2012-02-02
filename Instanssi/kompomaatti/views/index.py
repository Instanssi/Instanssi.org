# -*- coding: utf-8 -*-

from Instanssi.kompomaatti.misc.custom_render import custom_render
from Instanssi.kompomaatti.models import Compo
from datetime import datetime

def index(request):
    events = Compo.objects.filter(compo_start__gt=datetime.now()).order_by('compo_start')
    
    return custom_render(request, 'kompomaatti/index.html', {
        'events': events
    })