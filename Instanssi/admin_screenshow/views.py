# -*- coding: utf-8 -*-

from common.http import Http403
from common.auth import staff_access_required
from django.http import Http404,HttpResponseRedirect
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.admin_screenshow.forms import *
import os

# Logging related
import logging
logger = logging.getLogger(__name__)

@staff_access_required
def index(request, sel_event_id):
    return admin_render(request, "admin_screenshow/index.html", {
        'selected_event_id': int(sel_event_id),
    })
    
@staff_access_required
def config(request, sel_event_id):
    # Try to get configuration for event
    conf = None
    try:
        conf = ScreenConfig.objects.get(event_id=sel_event_id)
    except:
        pass
    
    # Handle post data
    if request.method == 'POST':
        # Check for permissions
        if not request.user.has_perm('screenshow.change_screenconfig'):
            raise Http403
         
        # Handle form
        configform = ScreenConfigForm(request.POST, instance=conf)
        if configform.is_valid():
            data = configform.save(commit=False)
            data.event_id = sel_event_id
            data.save()
            logger.info('Screenshow configuration changed.', extra={'user': request.user, 'event_id': sel_event_id})
            return HttpResponseRedirect(reverse('manage-screenshow:config', args=(sel_event_id,)))
    else:
        configform = ScreenConfigForm(instance=conf)
    
    # Dump template contents
    return admin_render(request, "admin_screenshow/config.html", {
        'selected_event_id': int(sel_event_id),
        'configform': configform,
    })

@staff_access_required
def playlist(request, sel_event_id):
    # Check for form data
    if request.method == 'POST':
        # Check for permissions
        if not request.user.has_perm('screenshow.add_playlistvideo'):
            raise Http403
        
        # Handle data
        playlistform = PlaylistVideoForm(request.POST)
        if playlistform.is_valid():
            data = playlistform.save(commit=False)
            data.event_id = sel_event_id
            data.save()
            logger.info('Video "'+data.name+'" added to playlist.', extra={'user': request.user, 'event_id': sel_event_id})
            return HttpResponseRedirect(reverse('manage-screenshow:playlist', args=(sel_event_id,)))
    else:
        playlistform = PlaylistVideoForm()
    
    # Get messages
    videos = PlaylistVideo.objects.filter(event_id=sel_event_id).order_by('-index')
    
    # Dump template
    return admin_render(request, "admin_screenshow/playlist.html", {
        'selected_event_id': int(sel_event_id),
        'videos': videos,
        'playlistform': playlistform,
    })
    
@staff_access_required
def playlist_edit(request, sel_event_id, video_id):
    # Check for permissions
    if not request.user.has_perm('screenshow.change_playlistvideo'):
        raise Http403
    
    # Get initial data
    playlist = get_object_or_404(PlaylistVideo, pk=video_id)
    
    # Check for form data
    if request.method == 'POST':
        playlistform = PlaylistVideoForm(request.POST, instance=playlist)
        if playlistform.is_valid():
            v = playlistform.save()
            logger.info('Video "'+v.name+'" edited on playlist.', extra={'user': request.user, 'event_id': sel_event_id})
            return HttpResponseRedirect(reverse('manage-screenshow:playlist', args=(sel_event_id,)))
    else:
        playlistform = PlaylistVideoForm(instance=playlist)
    
    # Dump template
    return admin_render(request, "admin_screenshow/playlist_edit.html", {
        'selected_event_id': int(sel_event_id),
        'video_id': int(video_id),
        'playlistform': playlistform,
    })
    
@staff_access_required
def playlist_delete(request, sel_event_id, video_id):
    # Check for permissions
    if not request.user.has_perm('screenshow.delete_playlistvideo'):
        raise Http403
    
    # Attempt to delete
    try:
        v = PlaylistVideo.objects.get(pk=video_id)
        v.delete()
        logger.info('Video "'+v.name+'" deleted from playlist.', extra={'user': request.user, 'event_id': sel_event_id})
    except PlaylistVideo.DoesNotExist:
        pass
    
    # Dump template
    return HttpResponseRedirect(reverse('manage-screenshow:playlist', args=(sel_event_id,)))


    

@staff_access_required
def ircmessages(request, sel_event_id):
    # Get messages
    messages = IRCMessage.objects.filter(event_id=sel_event_id)
    
    # Dump template
    return admin_render(request, "admin_screenshow/ircmessages.html", {
        'selected_event_id': int(sel_event_id),
        'messages': messages,
    })
    
@staff_access_required
def ircmessage_edit(request, sel_event_id, message_id):
    # Check for permissions
    if not request.user.has_perm('screenshow.change_ircmessage'):
        raise Http403
    
    # Get initial data
    message = get_object_or_404(IRCMessage, pk=message_id)
    
    # Check for form data
    if request.method == 'POST':
        messageform = IRCMessageForm(request.POST, instance=message)
        if messageform.is_valid():
            messageform.save()
            logger.info('IRC Message '+str(message.id)+' edited', extra={'user': request.user, 'event_id': sel_event_id})
            return HttpResponseRedirect(reverse('manage-screenshow:ircmessages', args=(sel_event_id,)))
    else:
        messageform = IRCMessageForm(instance=message)
    
    # Dump template
    return admin_render(request, "admin_screenshow/ircmessage_edit.html", {
        'selected_event_id': int(sel_event_id),
        'message_id': int(message_id),
        'messageform': messageform,
    })
    
@staff_access_required
def ircmessage_delete(request, sel_event_id, message_id):
    # Check for permissions
    if not request.user.has_perm('screenshow.delete_ircmessage'):
        raise Http403
    
    # Attempt to delete
    try:
        IRCMessage.objects.get(pk=message_id).delete()
        logger.info('IRC Message '+str(message_id)+' deleted.', extra={'user': request.user, 'event_id': sel_event_id})
    except Message.DoesNotExist:
        pass
    
    # Dump template
    return HttpResponseRedirect(reverse('manage-screenshow:ircmessages', args=(sel_event_id,)))



@staff_access_required
def messages(request, sel_event_id):
    # Check for form data
    if request.method == 'POST':
        # Check for permissions
        if not request.user.has_perm('screenshow.add_message'):
            raise Http403
        
        # Handle data
        messageform = MessageForm(request.POST)
        if messageform.is_valid():
            data = messageform.save(commit=False)
            data.event_id = sel_event_id
            data.save()
            logger.info('Message added.', extra={'user': request.user, 'event_id': sel_event_id})
            return HttpResponseRedirect(reverse('manage-screenshow:messages', args=(sel_event_id,)))
    else:
        messageform = MessageForm()
    
    # Get messages
    messages = Message.objects.filter(event_id=sel_event_id)
    
    # Dump template
    return admin_render(request, "admin_screenshow/messages.html", {
        'selected_event_id': int(sel_event_id),
        'messageform': messageform,
        'messages': messages,
    })
    
@staff_access_required
def message_edit(request, sel_event_id, message_id):
    # Check for permissions
    if not request.user.has_perm('screenshow.change_message'):
        raise Http403
    
    # Get initial data
    message = get_object_or_404(Message, pk=message_id)
    
    # Check for form data
    if request.method == 'POST':
        messageform = MessageForm(request.POST, instance=message)
        if messageform.is_valid():
            messageform.save()
            logger.info('Message edited.', extra={'user': request.user, 'event_id': sel_event_id})
            return HttpResponseRedirect(reverse('manage-screenshow:messages', args=(sel_event_id,)))
    else:
        messageform = MessageForm(instance=message)
    
    # Dump template
    return admin_render(request, "admin_screenshow/message_edit.html", {
        'selected_event_id': int(sel_event_id),
        'message_id': int(message_id),
        'messageform': messageform,
    })
    
@staff_access_required
def message_delete(request, sel_event_id, message_id):
    # Check for permissions
    if not request.user.has_perm('screenshow.delete_message'):
        raise Http403
    
    # Attempt to delete
    try:
        Message.objects.get(pk=message_id).delete()
        logger.info('Message deleted.', extra={'user': request.user, 'event_id': sel_event_id})
    except Message.DoesNotExist:
        pass
    
    # Dump template
    return HttpResponseRedirect(reverse('manage-screenshow:messages', args=(sel_event_id,)))


@staff_access_required
def sponsors(request, sel_event_id):
    # Check for form data
    if request.method == 'POST':
        # Check for permissions
        if not request.user.has_perm('screenshow.add_sponsor'):
            raise Http403
        
        # Handle data
        sponsorform = SponsorForm(request.POST, request.FILES)
        if sponsorform.is_valid():
            data = sponsorform.save(commit=False)
            data.event_id = sel_event_id
            data.save()
            logger.info('Sponsor "'+data.name+'" added.', extra={'user': request.user, 'event_id': sel_event_id})
            return HttpResponseRedirect(reverse('manage-screenshow:sponsors', args=(sel_event_id,)))
    else:
        sponsorform = SponsorForm()
    
    # Get sponsors
    sponsors = Sponsor.objects.filter(event_id=sel_event_id)
    
    # Dump template
    return admin_render(request, "admin_screenshow/sponsors.html", {
        'selected_event_id': int(sel_event_id),
        'sponsorform': sponsorform,
        'sponsors': sponsors,
    })

@staff_access_required
def sponsor_edit(request, sel_event_id, sponsor_id):
    # Check for permissions
    if not request.user.has_perm('screenshow.change_sponsor'):
        raise Http403
    
    # Get initial data
    sponsor = get_object_or_404(Sponsor, pk=sponsor_id)
    
    # Check for form data
    if request.method == 'POST':
        sponsorform = SponsorForm(request.POST, request.FILES, instance=sponsor)
        if sponsorform.is_valid():
            s = sponsorform.save()
            logger.info('Sponsor "'+s.name+'" edited.', extra={'user': request.user, 'event_id': sel_event_id})
            return HttpResponseRedirect(reverse('manage-screenshow:sponsors', args=(sel_event_id,)))
    else:
        sponsorform = SponsorForm(instance=sponsor)
    
    # Dump template
    return admin_render(request, "admin_screenshow/sponsor_edit.html", {
        'selected_event_id': int(sel_event_id),
        'sponsor_id': int(sponsor_id),
        'sponsorform': sponsorform,
    })
    
@staff_access_required
def sponsor_delete(request, sel_event_id, sponsor_id):
    # Check for permissions
    if not request.user.has_perm('screenshow.delete_sponsor'):
        raise Http403
    
    # Attempt to delete
    try:
        sponsor = Sponsor.objects.get(pk=sponsor_id)
        full_name = os.path.join(settings.MEDIA_ROOT, sponsor.logo.name)
        if sponsor.logo and os.path.exists(full_name):
            sponsor.logo.delete()
        sponsor.delete()
        logger.info('Sponsor "'+sponsor.name+'" deleted.', extra={'user': request.user, 'event_id': sel_event_id})
    except Sponsor.DoesNotExist:
        pass
    
    # Dump template
    return HttpResponseRedirect(reverse('manage-screenshow:sponsors', args=(sel_event_id,)))

