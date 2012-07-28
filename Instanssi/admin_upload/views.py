# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import Http404,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from models import UploadedFile
from forms import UploadForm
from datetime import datetime
from Instanssi.admin_base.misc.custom_render import admin_render

@login_required(login_url='/control/auth/login/')
def index(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Get filelist
    files = UploadedFile.objects.all()
    
    # Render response
    return admin_render(request, "admin_upload/index.html", {
        'files': files,
    })
    
@login_required(login_url='/control/auth/login/')
def deletefile(request, file_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Check for permissions
    if not request.user.has_perm('admin_upload.delete_uploadedfile'):
        raise Http404
    
    # Delete the file
    try:
        rec = UploadedFile.objects.get(id=file_id)
        rec.file.delete()
        rec.delete()
    except UploadedFile.DoesNotExist:
        pass
    
    return HttpResponseRedirect("/control/files/")
    
@login_required(login_url='/control/auth/login/')
def upload(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Check for permissions
    if not request.user.has_perm('admin_upload.add_uploadedfile'):
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
    return admin_render(request, "admin_upload/upload.html", {
        'uploadform': uploadform,
    })