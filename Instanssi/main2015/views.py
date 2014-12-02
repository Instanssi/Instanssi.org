# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext

def pageloader(request, templatename):
    return render_to_response('main2015/'+templatename+'.html', {
        'event_id': 8, 
        'templatename': templatename,
    }, context_instance=RequestContext(request))
