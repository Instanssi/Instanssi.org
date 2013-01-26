# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from common.responses import JSONResponse
from Instanssi.store.models import *

# Shows a simple error message
def error_page(request):
    return render_to_response('store/error.html', {
    }, context_instance=RequestContext(request))

# Shows a simple success message  
def success_page(request):
    return render_to_response('store/success.html', {
    }, context_instance=RequestContext(request))

# Handles the actual success notification from SVM
def notify_handler(request):
    return JSONResponse({})

# Should take care of JSON request from our own form, and then make the request to
# Suomen verkkomaksut JSON api.
def transaction_handler(request):
    return JSONResponse({'error': 'Method has not been implemented.'})

