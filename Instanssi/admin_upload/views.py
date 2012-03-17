# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from models import UploadedFile

@login_required
def index(request):
    # Make sure the user is superuser.
    if not request.user.is_superuser:
        raise Http404
    
    # Render response
    return render_to_response("admin_upload/index.html", {
    }, context_instance=RequestContext(request))
    
@login_required
def upload(request):
    # Make sure the user is superuser.
    if not request.user.is_superuser:
        raise Http404
    
    # Render response
    return render_to_response("admin_upload/upload.html", {
    }, context_instance=RequestContext(request))