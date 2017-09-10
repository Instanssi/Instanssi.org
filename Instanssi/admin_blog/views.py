# -*- coding: utf-8 -*-

from Instanssi.common.http import Http403
from Instanssi.common.auth import staff_access_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils import timezone
from Instanssi.ext_blog.models import BlogEntry
from Instanssi.admin_blog.forms import BlogEntryForm, BlogEntryEditForm
from Instanssi.admin_base.misc.custom_render import admin_render

# Logging related
import logging
logger = logging.getLogger(__name__)


@staff_access_required
def index(request, sel_event_id):
    # Post
    if request.method == 'POST':
        # Check for permissions
        if not request.user.has_perm('ext_blog.add_blogentry'):
            raise Http403
        
        # Handle form
        form = BlogEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.event_id = int(sel_event_id)
            entry.date = timezone.now()
            entry.user = request.user
            entry.save()
            logger.info('Blog entry "'+entry.title+'" added.', extra={'user': request.user, 'event_id': sel_event_id})
            return HttpResponseRedirect(reverse('manage-blog:index', args=(sel_event_id,)))
    else:
        form = BlogEntryForm()
    
    # Get events
    entries = BlogEntry.objects.filter(event_id = sel_event_id)
    
    # Render response
    return admin_render(request, "admin_blog/index.html", {
        'entries': entries,
        'selected_event_id': int(sel_event_id),
        'addform': form,
    })


@staff_access_required
def edit(request, sel_event_id, entry_id):
    # Check for permissions
    if not request.user.has_perm('ext_blog.change_blogentry'):
        raise Http403
    
    # Get old entry
    entry = get_object_or_404(BlogEntry, pk=entry_id)
    
    # Go ahead and edit
    if request.method == 'POST':
        form = BlogEntryEditForm(request.POST, instance=entry)
        if form.is_valid():
            entry = form.save()
            logger.info('Blog entry "'+entry.title+'" edited.', extra={'user': request.user, 'event_id': sel_event_id})
            return HttpResponseRedirect(reverse('manage-blog:index', args=(sel_event_id,)))
    else:
        form = BlogEntryEditForm(instance=entry)
    
    # Render response
    return admin_render(request, "admin_blog/edit.html", {
        'editform': form,
        'selected_event_id': int(sel_event_id),
    })
    
    
@staff_access_required
def delete(request, sel_event_id, entry_id):
    # Check for permissions
    if not request.user.has_perm('ext_blog.delete_blogentry'):
        raise Http403
    
    # Delete entry
    try:
        entry = BlogEntry.objects.get(id=entry_id)
        entry.delete()
        logger.info('Blog entry "'+entry.title+'" deleted.', extra={'user': request.user, 'event_id': sel_event_id})
    except BlogEntry.DoesNotExist:
        pass
    
    return HttpResponseRedirect(reverse('manage-blog:index', args=(sel_event_id,)))
