# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import Http404,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from Instanssi.ext_blog.models import BlogEntry, BlogComment
from forms import BlogEntryForm
from datetime import datetime
from Instanssi.settings import SHORT_LANGUAGE_CODE

@login_required(login_url='/control/auth/login/')
def index(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    entries = BlogEntry.objects.all()
    
    # Render response
    return render_to_response("admin_blog/index.html", {
        'entries': entries,
    }, context_instance=RequestContext(request))

@login_required(login_url='/control/auth/login/')
def write(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Check for permissions
    if not request.user.has_perm('admin_blog.add_blogentry'):
        raise Http404
    
    if request.method == 'POST':
        form = BlogEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.date = datetime.now()
            entry.user = request.user
            entry.save()
            return HttpResponseRedirect("/control/blog/")
    else:
        form = BlogEntryForm()
    
    # Render response
    return render_to_response("admin_blog/write.html", {
        'addform': form,
        'LANGUAGE_CODE': SHORT_LANGUAGE_CODE,
    }, context_instance=RequestContext(request))

@login_required(login_url='/control/auth/login/')
def edit(request, entry_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Check for permissions
    if not request.user.has_perm('admin_blog.change_blogentry'):
        raise Http404
    
    # Get old entry
    try:
        entry = BlogEntry.objects.get(id=entry_id)
    except BlogEntry.DoesNotExist:
        raise Http404
    
    # Go ahead and edit
    if request.method == 'POST':
        form = BlogEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/control/blog/")
    else:
        form = BlogEntryForm(instance=entry)
    
    # Render response
    return render_to_response("admin_blog/edit.html", {
        'editform': form,
        'LANGUAGE_CODE': SHORT_LANGUAGE_CODE,
    }, context_instance=RequestContext(request))
    
    
@login_required(login_url='/control/auth/login/') 
def delete(request, entry_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Check for permissions
    if not request.user.has_perm('admin_blog.delete_blogentry'):
        raise Http404
    
    # Delete entry
    try:
        entry = BlogEntry.objects.get(id=entry_id)
        entry.delete()
    except BlogEntry.DoesNotExist:
        pass
    
    return HttpResponseRedirect("/control/blog/")
