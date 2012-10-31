# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import Http404,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from Instanssi.ext_blog.models import BlogEntry, BlogComment
from Instanssi.kompomaatti.models import Event
from forms import BlogEntryForm
from datetime import datetime
from django.conf import settings
from Instanssi.admin_base.misc.custom_render import admin_render

@login_required(login_url='/manage/auth/login/')
def index(request, sel_event_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Post
    if request.method == 'POST':
        # Check for permissions
        if not request.user.has_perm('admin_blog.add_blogentry'):
            raise Http404
        
        # Handle form
        form = BlogEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.event_id = int(sel_event_id)
            entry.date = datetime.now()
            entry.user = request.user
            entry.save()
            return HttpResponseRedirect("/manage/"+sel_event_id+"/blog/")
    else:
        form = BlogEntryForm()
    
    # Get events
    entries = BlogEntry.objects.filter(event_id = sel_event_id)
    
    # Render response
    return admin_render(request, "admin_blog/index.html", {
        'entries': entries,
        'selected_event_id': int(sel_event_id),
        'addform': form,
        'LANGUAGE_CODE': getattr(settings, 'SHORT_LANGUAGE_CODE'),
    })

@login_required(login_url='/manage/auth/login/')
def edit(request, sel_event_id, entry_id):
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
            entry = form.save(commit=False)
            entry.date = datetime.now()
            entry.save()
            return HttpResponseRedirect("/manage/"+sel_event_id+"/blog/")
    else:
        form = BlogEntryForm(instance=entry)
    
    # Render response
    return admin_render(request, "admin_blog/edit.html", {
        'editform': form,
        'LANGUAGE_CODE': getattr(settings, 'SHORT_LANGUAGE_CODE'),
        'selected_event_id': int(sel_event_id),
    })
    
    
@login_required(login_url='/manage/auth/login/') 
def delete(request, sel_event_id, entry_id):
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
    
    return HttpResponseRedirect("/manage/"+sel_event_id+"/blog/")
