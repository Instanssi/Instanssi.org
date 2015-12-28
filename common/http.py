# -*- coding: utf-8 -*-

from django.template import RequestContext, loader
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden  

# A custom Http403 exception
# from http://theglenbot.com/creating-a-custom-http403-exception-in-django/


class Http403(Exception):    
    pass


def render_to_403(*args, **kwargs):     
    if not isinstance(args, list):
        args = []         
        args.append('403.html')              

    httpresponse_kwargs = {'content_type': kwargs.pop('content_type', None)}          
    response = HttpResponseForbidden(loader.render_to_string(*args, **kwargs), **httpresponse_kwargs)              

    return response  


class Http403Middleware(object):     
    def process_exception(self, request, exception):
        if isinstance(exception, Http403):
            if getattr(settings, 'DEBUG'):
                raise PermissionDenied             
            return render_to_403(context_instance=RequestContext(request))      
