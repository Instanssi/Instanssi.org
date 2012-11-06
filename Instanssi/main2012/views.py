# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext

def pageloader(request, templatename):
    return render_to_response('main2012/'+templatename+'.html', context_instance=RequestContext(request))