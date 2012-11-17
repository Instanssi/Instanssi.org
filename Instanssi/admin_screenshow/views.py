# -*- coding: utf-8 -*-

from common.http import Http403
from django.http import Http404,HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.admin_base.misc.auth_decorator import staff_access_required
from Instanssi.admin_screenshow.forms import *

@staff_access_required
def index(request, sel_event_id):
    return admin_render(request, "admin_screenshow/index.html", {
        'selected_event_id': int(sel_event_id),
    })

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
            sponsorform.save()
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
        sponsor.logo.delete()
        sponsor.delete()
    except Sponsor.DoesNotExist:
        pass
    
    # Dump template
    return HttpResponseRedirect(reverse('manage-screenshow:sponsors', args=(sel_event_id,)))

