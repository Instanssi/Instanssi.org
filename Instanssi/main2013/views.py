# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext
from Instanssi.store.store_renderer import render_store
from django.core.urlresolvers import reverse

def pageloader(request, templatename):
    return render_to_response('main2013/'+templatename+'.html', {
        'event_id': 5, 
        'templatename': templatename,
        'is_secure': request.is_secure(),
    }, context_instance=RequestContext(request))
    
def tickets(request):
    # Handle store request
    domain = u'http://instanssi.org'
    success_url = reverse('main2013:store_success')
    failure_url = reverse('main2013:store_failure')
    ret = render_store(request, 5, domain, success_url, failure_url)
    if type(ret) is not dict:
        return ret
    
    # Template variables
    vars = {
        'event_id': 5, 
        'templatename': 'liput',
        'is_secure': request.is_secure(),
    }
    
    # Render page
    return render_to_response('main2013/liput.html', dict(vars.items() + ret.items()), context_instance=RequestContext(request))