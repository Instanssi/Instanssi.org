# -*- coding: utf-8 -*-

from common.http import Http403
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.conf import settings
from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.kompomaatti.models import Event, Entry, Compo, Competition, CompetitionParticipation, Vote
from Instanssi.arkisto.models import OtherVideo,OtherVideoCategory
from Instanssi.admin_arkisto.forms import VideoForm, VideoCategoryForm
from Instanssi.admin_arkisto.misc import utils

@login_required(login_url=getattr(settings, 'ADMIN_LOGIN_URL'))
def index(request, sel_event_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
    
    # Render response
    return admin_render(request, "admin_arkisto/index.html", {
        'selected_event_id': int(sel_event_id),
    })

@login_required(login_url=getattr(settings, 'ADMIN_LOGIN_URL'))
def removeoldvotes(request, sel_event_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
    
    # Check rights
    if not request.user.has_perms('kompomaatti.delete_vote'):
        raise Http403
    
    # Don't proceed if the event is still ongoing
    if utils.is_event_ongoing(get_object_or_404(Event, pk=int(sel_event_id))):
        raise Http404
    
    # Find compos belonging to this event
    compo_ids = Compo.objects.filter(event_id=int(sel_event_id)).values('pk')
    
    # Don't allow removing votes if votes haven't yet been consolidated to entry rows (prevent data loss)
    if utils.is_votes_unoptimized(compo_ids):
        raise Http404
    
    # Delete votes belonging to compos in this event
    Vote.objects.filter(compo__in=compo_ids).delete()
    
    # All done, redirect
    return HttpResponseRedirect(reverse('admin-archiver', args=(sel_event_id)))

@login_required(login_url=getattr(settings, 'ADMIN_LOGIN_URL'))
def transferrights(request, sel_event_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
    
    # Check rights
    if not request.user.has_perms('kompomaatti.change_entry'):
        raise Http403
    
    # Don't allow this function if the event is still ongoing
    if utils.is_event_ongoing(get_object_or_404(Event, pk=int(sel_event_id))):
        raise Http404
    
    # Get archive user, compo id's and competition id's
    archiveuser = get_object_or_404(User, username="arkisto")
    compo_ids = Compo.objects.filter(event_id=int(sel_event_id)).values('pk')
    competition_ids = Competition.objects.filter(event_id=int(sel_event_id)).values('pk')
    
    # Transfer all user rights on entries belonging to this event
    entries = Entry.objects.filter(compo__in=compo_ids)
    for entry in entries:
        entry.user = archiveuser
        entry.save()
    
    # Transfer all competition participations to archive user
    participations = CompetitionParticipation.objects.filter(competition__in=competition_ids)
    for part in participations:
        part.user = archiveuser
        part.save()
    
    # All done, redirect
    return HttpResponseRedirect(reverse('admin-archiver', args=(sel_event_id)))
    
@login_required(login_url=getattr(settings, 'ADMIN_LOGIN_URL'))
def optimizescores(request, sel_event_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403

    # Check rights
    if not request.user.has_perms('kompomaatti.change_entry'):
        raise Http403
    
    # Don't allow this function if the event is still ongoing
    if utils.is_event_ongoing(get_object_or_404(Event, pk=int(sel_event_id))):
        raise Http404
    
    # Get compo id's
    compo_ids = Compo.objects.filter(event_id=int(sel_event_id)).values('pk')
    
    # Set score and rank to database, instead of having to calculate it every time we need it
    entries = Entry.objects.filter(compo__in=compo_ids)
    for entry in entries:
        entry.archive_rank = entry.get_rank()
        entry.archive_score = entry.get_score()
        entry.save()

    return HttpResponseRedirect(reverse('admin-archiver', args=(sel_event_id)))

@login_required(login_url=getattr(settings, 'ADMIN_LOGIN_URL'))
def archiver(request, sel_event_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
    
    # Get event information
    event = get_object_or_404(Event, pk=sel_event_id)
    
    # Get archive user information for future use
    archiveuser = get_object_or_404(User, username="arkisto")
    
    # Get Compo id's belonging to this event for future use
    compo_ids = Compo.objects.filter(event_id=int(sel_event_id)).values('pk')
    
    # Check if there are any compo entries that are not owner by archive user
    untransferred = False
    entries = Entry.objects.filter(compo__in=compo_ids)
    for entry in entries:
        if entry.user != archiveuser:
            untransferred = True
            break
    
    # Check if there are any participations that are not owner by archive user
    if not untransferred:
        competition_ids = Competition.objects.filter(event_id=int(sel_event_id)).values('pk')
        participations = CompetitionParticipation.objects.filter(competition__in=competition_ids)
        for part in participations:
            if part.user != archiveuser:
                untransferred = True
                break

    # Check if voting results need to be optimized
    votes_unoptimized = utils.is_votes_unoptimized(compo_ids)

    # Check if event is still ongoing
    ongoing_activity = utils.is_event_ongoing(event)

    # See if there are any old votes left
    old_votes_found = False
    votes = Vote.objects.filter(compo__in=compo_ids)
    if len(votes) > 0:
        old_votes_found = True

    # Render response
    return admin_render(request, "admin_arkisto/archiver.html", {
        'selected_event_id': int(sel_event_id),
        'is_archived': event.archived,
        'untransferred': untransferred,
        'ongoing_activity': ongoing_activity,
        'votes_unoptimized': votes_unoptimized,
        'old_votes_found': old_votes_found,
    })
    
@login_required(login_url=getattr(settings, 'ADMIN_LOGIN_URL'))
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
    
    return HttpResponseRedirect(reverse('admin-archiver', args=(sel_event_id)))

@login_required(login_url=getattr(settings, 'ADMIN_LOGIN_URL'))
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
    
    return HttpResponseRedirect(reverse('admin-archiver', args=(sel_event_id)))

@login_required(login_url=getattr(settings, 'ADMIN_LOGIN_URL'))
def vids(request, sel_event_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
    
    # Get event
    event = get_object_or_404(Event, pk=sel_event_id)
    
    # Handle form
    if request.method == "POST":
        # Check for permissions
        if not request.user.has_perm('arkisto.add_othervideo'):
            raise Http403
        
        # Handle form
        vidform = VideoForm(request.POST, event=event)
        if vidform.is_valid():
            vidform.save()
            return HttpResponseRedirect(reverse('admin-vids', args=(sel_event_id)))
    else:
        vidform = VideoForm(event=event)
    
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
    
@login_required(login_url=getattr(settings, 'ADMIN_LOGIN_URL'))
def editvid(request, sel_event_id, video_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
    
    # Check for permissions
    if not request.user.has_perm('arkisto.change_othervideo'):
        raise Http403
    
    # Get Video
    video = get_object_or_404(OtherVideo, pk=video_id)
    
    # Get event
    event = get_object_or_404(Event, pk=sel_event_id)
    
    # Handle form
    if request.method == "POST":
        vidform = VideoForm(request.POST, instance=video, event=event)
        if vidform.is_valid():
            vidform.save()
            return HttpResponseRedirect(reverse('admin-vids', args=(sel_event_id)))
    else:
        vidform = VideoForm(instance=video, event=event)
    
    # Render response
    return admin_render(request, "admin_arkisto/editvid.html", {
        'vidform': vidform,
        'vid': video,
        'selected_event_id': int(sel_event_id),
    })
    
    
@login_required(login_url=getattr(settings, 'ADMIN_LOGIN_URL'))
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
    return HttpResponseRedirect(reverse('admin-vids', args=(sel_event_id)))
    
@login_required(login_url=getattr(settings, 'ADMIN_LOGIN_URL'))
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
            return HttpResponseRedirect(reverse('admin-vidcats', args=(sel_event_id)))
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
    
@login_required(login_url=getattr(settings, 'ADMIN_LOGIN_URL'))
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
            return HttpResponseRedirect(reverse('admin-vidcats', args=(sel_event_id)))
    else:
        catform = VideoCategoryForm(instance=category)
    
    # Render response
    return admin_render(request, "admin_arkisto/editcat.html", {
        'catform': catform,
        'cat': category,
        'selected_event_id': int(sel_event_id),
    })
    
@login_required(login_url=getattr(settings, 'ADMIN_LOGIN_URL'))
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
    return HttpResponseRedirect(reverse('admin-vidcats', args=(sel_event_id)))
