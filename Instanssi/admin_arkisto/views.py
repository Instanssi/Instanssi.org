# -*- coding: utf-8 -*-

from common.http import Http403
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.kompomaatti.models import Event
from Instanssi.arkisto.models import OtherVideo,OtherVideoCategory
from Instanssi.admin_arkisto.forms import VideoForm, VideoCategoryForm

@login_required(login_url='/manage/auth/login/')
def archiver(request, sel_event_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
    
    # Get event information
    event = get_object_or_404(Event, pk=sel_event_id)

    # Render response
    return admin_render(request, "admin_arkisto/archiver.html", {
        'selected_event_id': int(sel_event_id),
        'is_archived': event.archived,
    })
    
@login_required(login_url='/manage/auth/login/')
def show(request, sel_event_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
    
    # Check rights
    if not request.user.has_perms('kompomaatti.change_event'):
        raise Http403
    
    # Mark event as archived
    event = get_object_or_404(Event, pk=sel_event_id)
    event.archived = True
    event.save()
    
    return HttpResponseRedirect("/manage/"+sel_event_id+"/arkisto/archiver/")

@login_required(login_url='/manage/auth/login/')
def hide(request, sel_event_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
    
    # Check rights
    if not request.user.has_perms('kompomaatti.change_event'):
        raise Http403
    
    # Mark event as NOT archived
    event = get_object_or_404(Event, pk=sel_event_id)
    event.archived = False
    event.save()
    
    return HttpResponseRedirect("/manage/"+sel_event_id+"/arkisto/archiver/")

@login_required(login_url='/manage/auth/login/')
def vids(request, sel_event_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
    
    # Handle form
    if request.method == "POST":
        # Check for permissions
        if not request.user.has_perm('arkisto.add_othervideo'):
            raise Http403
        
        # Handle form
        vidform = VideoForm(request.POST)
        if vidform.is_valid():
            vidform.save()
            return HttpResponseRedirect("/manage/"+sel_event_id+"/arkisto/vids/")
    else:
        vidform = VideoForm()
    
    # Get videos belonging to selected event
    categories = OtherVideoCategory.objects.filter(event_id=int(sel_event_id))
    videos = []
    for cat in categories:
        vlist = OtherVideo.objects.filter(category=cat)
        for video in vlist:
            videos.append(video)
    
    # Render response
    return admin_render(request, "admin_arkisto/vids.html", {
        'videos': videos,
        'vidform': vidform,
        'selected_event_id': int(sel_event_id),
    })
    
@login_required(login_url='/manage/auth/login/')
def editvid(request, sel_event_id, video_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
    
    # Check for permissions
    if not request.user.has_perm('arkisto.change_othervideo'):
        raise Http403
    
    # Get Video
    video = get_object_or_404(OtherVideo, pk=video_id)
    
    # Handle form
    if request.method == "POST":
        vidform = VideoForm(request.POST, instance=video)
        if vidform.is_valid():
            vidform.save()
            return HttpResponseRedirect("/manage/"+sel_event_id+"/arkisto/vids/")
    else:
        vidform = VideoForm(instance=video)
    
    # Render response
    return admin_render(request, "admin_arkisto/editvid.html", {
        'vidform': vidform,
        'vid': video,
        'selected_event_id': int(sel_event_id),
    })
    
    
@login_required(login_url='/manage/auth/login/')
def deletevid(request, sel_event_id, video_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
    
    # Check for permissions
    if not request.user.has_perm('arkisto.delete_othervideo'):
        raise Http403
    
    # Attempt to delete video
    try:
        OtherVideo.objects.get(id=video_id).delete()
    except:
        pass
    
    # Redirect
    return HttpResponseRedirect("/manage/"+sel_event_id+"/arkisto/vids/")
    
@login_required(login_url='/manage/auth/login/')
def cats(request, sel_event_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
    
    # Handle form
    if request.method == "POST":
        # Check for permissions
        if not request.user.has_perm('arkisto.add_othervideocategory'):
            raise Http403
        
        # Handle form
        catform = VideoCategoryForm(request.POST)
        if catform.is_valid():
            cat = catform.save(commit=False)
            cat.event_id = int(sel_event_id)
            cat.save()
            return HttpResponseRedirect("/manage/"+sel_event_id+"/arkisto/vidcats/")
    else:
        catform = VideoCategoryForm()
    
    # Get videos belonging to selected event
    categories = OtherVideoCategory.objects.filter(event_id=int(sel_event_id))
    
    # Render response
    return admin_render(request, "admin_arkisto/cats.html", {
        'categories': categories,
        'catform': catform,
        'selected_event_id': int(sel_event_id),
    })
    
@login_required(login_url='/manage/auth/login/')
def editcat(request, sel_event_id, category_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
    
    # Check for permissions
    if not request.user.has_perm('arkisto.change_othervideocategory'):
        raise Http403
    
    # Get category
    category = get_object_or_404(OtherVideoCategory, pk=category_id)
    
    # Handle form
    if request.method == "POST":
        catform = VideoCategoryForm(request.POST, instance=category)
        if catform.is_valid():
            catform.save()
            return HttpResponseRedirect("/manage/"+sel_event_id+"/arkisto/vidcats/")
    else:
        catform = VideoCategoryForm(instance=category)
    
    # Render response
    return admin_render(request, "admin_arkisto/editcat.html", {
        'catform': catform,
        'cat': category,
        'selected_event_id': int(sel_event_id),
    })
    
@login_required(login_url='/manage/auth/login/')
def deletecat(request, sel_event_id, category_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
    
    # Check for permissions
    if not request.user.has_perm('arkisto.delete_othervideocategory'):
        raise Http403
    
    # Attempt to delete category
    try:
        OtherVideoCategory.objects.get(id=category_id).delete()
    except:
        pass
    
    # Redirect
    return HttpResponseRedirect("/manage/"+sel_event_id+"/arkisto/vidcats/")
