# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import Http404,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.kompomaatti.models import Event
from Instanssi.arkisto.models import OtherVideo,OtherVideoCategory
from Instanssi.admin_base.misc.eventsel import get_selected_event
from Instanssi.admin_arkisto.forms import VideoForm, VideoCategoryForm

@login_required(login_url='/manage/auth/login/')
def index(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    events = Event.objects.all()
    
    # Render response
    return admin_render(request, "admin_arkisto/index.html", {
        'events': events,
    })

@login_required(login_url='/manage/auth/login/')
def archiver(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404

    # Render response
    return admin_render(request, "admin_arkisto/archiver.html", {})

@login_required(login_url='/manage/auth/login/')
def vids(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Get videos belonging to selected event
    selected_event_id = get_selected_event(request)
    categories = OtherVideoCategory.objects.filter(event_id=selected_event_id)
    videos = []
    for cat in categories:
        vlist = OtherVideo.objects.filter(category=cat)
        for video in vlist:
            videos.append(video)
    
    # Render response
    return admin_render(request, "admin_arkisto/vids.html", {
        'videos': videos,
    })
    
@login_required(login_url='/manage/auth/login/')
def addvid(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Check for permissions
    if not request.user.has_perm('arkisto.add_othervideo'):
        raise Http404
    
    # Handle form
    if request.method == "POST":
        vidform = VideoForm(request.POST)
        if vidform.is_valid():
            vidform.save()
            return HttpResponseRedirect("/control/arkisto/vids/")
    else:
        vidform = VideoForm()
    
    # Render response
    return admin_render(request, "admin_arkisto/addvid.html", {
        'vidform': vidform,                                             
    })
    
@login_required(login_url='/manage/auth/login/')
def editvid(request, video_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Check for permissions
    if not request.user.has_perm('arkisto.change_othervideo'):
        raise Http404
    
    # Get Video
    try:
        video = OtherVideo.objects.get(id=video_id)
    except:
        raise Http404
    
    # Handle form
    if request.method == "POST":
        vidform = VideoForm(request.POST, instance=video)
        if vidform.is_valid():
            vidform.save()
            return HttpResponseRedirect("/control/arkisto/vids/")
    else:
        vidform = VideoForm(instance=video)
    
    # Render response
    return admin_render(request, "admin_arkisto/editvid.html", {
        'vidform': vidform,
        'vid': video,                                          
    })
    
    
@login_required(login_url='/manage/auth/login/')
def deletevid(request, video_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Check for permissions
    if not request.user.has_perm('arkisto.delete_othervideo'):
        raise Http404
    
    # Attempt to delete video
    try:
        OtherVideo.objects.get(id=video_id).delete()
    except:
        pass
    
    # Redirect
    return HttpResponseRedirect("/control/arkisto/vids/")
    
@login_required(login_url='/manage/auth/login/')
def cats(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Get videos belonging to selected event
    selected_event_id = get_selected_event(request)
    categories = OtherVideoCategory.objects.filter(event_id=selected_event_id)
    
    # Render response
    return admin_render(request, "admin_arkisto/cats.html", {
        'categories': categories,
    })
    
@login_required(login_url='/manage/auth/login/')
def addcat(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Check for permissions
    if not request.user.has_perm('arkisto.add_othervideocategory'):
        raise Http404
    
    # Handle form
    if request.method == "POST":
        catform = VideoCategoryForm(request.POST)
        if catform.is_valid():
            cat = catform.save(commit=False)
            cat.event_id = get_selected_event(request)
            cat.save()
            return HttpResponseRedirect("/control/arkisto/vidcats/")
    else:
        catform = VideoCategoryForm()
    
    # Render response
    return admin_render(request, "admin_arkisto/addcat.html", {
        'catform': catform,
    })
    
@login_required(login_url='/manage/auth/login/')
def editcat(request, category_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Check for permissions
    if not request.user.has_perm('arkisto.change_othervideocategory'):
        raise Http404
    
    # Get category
    try:
        category = OtherVideoCategory.objects.get(id=category_id)
    except:
        raise Http404
    
    # Handle form
    if request.method == "POST":
        catform = VideoCategoryForm(request.POST, instance=category)
        if catform.is_valid():
            catform.save()
            return HttpResponseRedirect("/control/arkisto/vidcats/")
    else:
        catform = VideoCategoryForm(instance=category)
    
    # Render response
    return admin_render(request, "admin_arkisto/editcat.html", {
        'catform': catform,
        'cat': category,
    })
    
@login_required(login_url='/manage/auth/login/')
def deletecat(request, category_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Check for permissions
    if not request.user.has_perm('arkisto.delete_othervideocategory'):
        raise Http404
    
    # Attempt to delete category
    try:
        OtherVideoCategory.objects.get(id=category_id).delete()
    except:
        pass
    
    # Redirect
    return HttpResponseRedirect("/control/arkisto/vidcats/")
