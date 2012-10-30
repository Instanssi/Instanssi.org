# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import Http404,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from Instanssi.admin_upload.models import UploadedFile
from Instanssi.admin_upload.forms import UploadForm
from Instanssi.admin_base.misc.custom_render import admin_render
from datetime import datetime

@login_required(login_url='/manage/auth/login/')
def index(request, sel_event_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Handle form data, if any
    if request.method == 'POST':
        # Check for permissions
        if not request.user.has_perm('admin_upload.add_uploadedfile'):
            raise Http404
        
        # Handle form
        uploadform = UploadForm(request.POST, request.FILES)
        if uploadform.is_valid():
            data = uploadform.save(commit=False)
            data.user = request.user
            data.date = datetime.now()
            data.event_id = int(sel_event_id)
            data.save()
            return HttpResponseRedirect("/manage/"+sel_event_id+"/files/")
    else:
        uploadform = UploadForm()
    
    # Get filelist
    files = UploadedFile.objects.filter(event_id=sel_event_id)
    
    # Render response
    return admin_render(request, "admin_upload/index.html", {
        'files': files,
        'uploadform': uploadform,
        'selected_event_id': int(sel_event_id),
    })
    
@login_required(login_url='/manage/auth/login/')
def deletefile(request, sel_event_id, file_id):
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
    
    return HttpResponseRedirect("/manage/"+sel_event_id+"/files/")
    
@login_required(login_url='/manage/auth/login/')
def editfile(request, sel_event_id, file_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Check for permissions
    if not request.user.has_perm('admin_upload.change_uploadedfile'):
        raise Http404
    
    # Get previously uploaded file
    try:
        uploadedfile = UploadedFile.objects.get(id=file_id)
    except:
        raise Http404
    
    # Handle form data
    if request.method == 'POST':
        uploadform = UploadForm(request.POST, request.FILES, instance=uploadedfile)
        if uploadform.is_valid():
            uploadform.save()
            return HttpResponseRedirect("/manage/"+sel_event_id+"/files/")
    else:
        uploadform = UploadForm(instance=uploadedfile)
    
    # Render response
    return admin_render(request, "admin_upload/edit.html", {
        'uploadform': uploadform,
        'selected_event_id': int(sel_event_id),
    })