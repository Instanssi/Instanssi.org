# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import Http404,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from models import UploadedFile
from forms import UploadForm
from datetime import datetime

@login_required
def index(request):
    # Make sure the user is superuser.
    if not request.user.is_superuser:
        raise Http404
    
    # Get filelist
    files = UploadedFile.objects.all()
    
    # Render response
    return render_to_response("admin_upload/index.html", {
        'files': files,
    }, context_instance=RequestContext(request))
    
@login_required
def upload(request):
    # Make sure the user is superuser.
    if not request.user.is_superuser:
        raise Http404
    
    # Handle form data, if any
    if request.method == 'POST':
        uploadform = UploadForm(request.POST, request.FILES)
        if uploadform.is_valid():
            data = uploadform.save(commit=False)
            data.user = request.user
            data.date = datetime.now()
            data.save()
            return HttpResponseRedirect("/control/files/upload/")
    else:
        uploadform = UploadForm()
    
    # Render response
    return render_to_response("admin_upload/upload.html", {
        'uploadform': uploadform,
    }, context_instance=RequestContext(request))