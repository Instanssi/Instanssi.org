# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse

def pageloader(request, templatename):
    return render_to_response('main2014/'+templatename+'.html', {
        'event_id': 8, 
        'templatename': templatename,
    }, context_instance=RequestContext(request))
    