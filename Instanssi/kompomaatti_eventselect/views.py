# -*- coding: utf-8 -*-

from Instanssi.kompomaatti.models import Event
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

def index(request):
    # Check if user selected an event without Javascript
    if request.method == 'POST':
        event_id = int(request.POST['eventsel'])
        return HttpResponseRedirect(reverse('km:index', args=(event_id,)))
    
    # Render page
    return render_to_response('kompomaatti_eventselect/index.html', {
        'events': Event.objects.all().order_by('-date'),
    }, context_instance=RequestContext(request))
