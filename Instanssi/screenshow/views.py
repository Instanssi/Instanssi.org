# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext
from common.responses import JSONResponse

def index(request):
    return render_to_response('screenshow/index.html', context_instance=RequestContext(request))

def api(request):
    return JSONResponse({'test': 'ok'});