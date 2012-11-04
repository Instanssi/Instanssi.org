# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext

def login(request):
    return render_to_response('kompomaatti_auth/index.html', {}, context_instance=RequestContext(request))

def error(request):
    return render_to_response('kompomaatti_auth/error.html', {}, context_instance=RequestContext(request))
