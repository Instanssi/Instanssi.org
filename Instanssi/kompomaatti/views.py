# -*- coding: utf-8 -*-

from common.http import Http403
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from Instanssi.kompomaatti.misc.custom_render import custom_render
from Instanssi.kompomaatti.forms import ProfileForm, VoteCodeRequestForm, VoteCodeAssocForm
from Instanssi.kompomaatti.misc.auth_decorator import user_access_required
from Instanssi.kompomaatti.models import Event, Profile
from django.contrib.auth import logout
    
def index(request, event_id):
    return custom_render(request, 'kompomaatti/index.html', {
        'sel_event_id': int(event_id),
    })
    
def compos(request, event_id):
    return custom_render(request, 'kompomaatti/compos.html', {
        'sel_event_id': int(event_id),
    })
    
def compo_details(request, event_id, compo_id):
    return custom_render(request, 'kompomaatti/compo_details.html', {
        'sel_event_id': int(event_id),
    })
    
def competitions(request, event_id):
    return custom_render(request, 'kompomaatti/competitions.html', {
        'sel_event_id': int(event_id),
    })
    
def competition_details(request, event_id, competition_id):
    return custom_render(request, 'kompomaatti/competition_details.html', {
        'sel_event_id': int(event_id),
    })

def login(request, event_id):
    return custom_render(request, 'kompomaatti/login.html', {
        'sel_event_id': int(event_id),
    })

@user_access_required
def profile(request, event_id):
    # Get event
    event = get_object_or_404(Event, pk=int(event_id))
        
    # Check if user has the right to vote
    can_vote = False
    try:
        votecode = VoteCode.objects.get(event=event, associated_to=request.user)
        can_vote = True
    except:
        pass
        
    # Check if request for vote code has been made
    request_made = False
    try:
        vcreq = VoteCodeRequest.objects.get(event=event, user=request.user)
        request_made = True
    except:
        pass
        
    # Profile form
    if request.method == 'POST':
        profileform = ProfileForm(request.POST, prefix='prof', instance=request.user, user=request.user)
        if profileform.is_valid():
            profileform.save()
            return HttpResponseRedirect(reverse('kompomaatti-profile', args=(event_id,)))
    else:
        profileform = ProfileForm(instance=request.user, prefix='prof', user=request.user)
    
    # Votecode Association form
    if request.method == 'POST':
        votecodeassocform = VoteCodeAssocForm(request.POST, prefix='vcassoc')
        if votecodeassocform.is_valid():
            votecodeassocform.save()
            return HttpResponseRedirect(reverse('kompomaatti-profile', args=(event_id,)))
    else:
        votecodeassocform = VoteCodeAssocForm(prefix='vcassoc')
    
    # Votecode Request form
    if request.method == 'POST':
        votecoderequestform = VoteCodeRequestForm(request.POST, prefix='vcreq')
        if votecoderequestform.is_valid():
            vcr = votecoderequestform.save(commit=False)
            vcr.user = request.user
            vcr.event = event
            vcr.save()
            return HttpResponseRedirect(reverse('kompomaatti-profile', args=(event_id,)))
    else:
        votecoderequestform = VoteCodeRequestForm(prefix='vcreq')
    
    # Render
    return custom_render(request, 'kompomaatti/profile.html', {
        'sel_event_id': int(event_id),
        'profileform': profileform,
        'votecodeassocform': votecodeassocform,
        'votecoderequestform': votecoderequestform,
        'can_vote': can_vote,
        'request_made': request_made,
    })
    
@user_access_required
def do_logout(request, event_id):
    logout(request)
    return HttpResponseRedirect(reverse('kompomaatti-index', args=(event_id,)))

