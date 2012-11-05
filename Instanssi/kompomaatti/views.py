# -*- coding: utf-8 -*-

from common.http import Http403
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from Instanssi.kompomaatti.misc.custom_render import custom_render
from Instanssi.kompomaatti.misc.auth_decorator import user_access_required
from Instanssi.kompomaatti.forms import *
from Instanssi.kompomaatti.models import *
from Instanssi.kompomaatti.misc.time_formatting import *
from django.contrib.auth import logout
from datetime import datetime
    
def index(request, event_id):
    return custom_render(request, 'kompomaatti/index.html', {
        'sel_event_id': int(event_id),
    })
    
def compos(request, event_id):
    # Get compos, format times
    compos = []
    for compo in Compo.objects.filter(active=True, event_id=int(event_id)):
        compos.append(compo_times_formatter(compo))
    
    # Dump the template
    return custom_render(request, 'kompomaatti/compos.html', {
        'sel_event_id': int(event_id),
        'compos': compos,
    })
    
def compo_details(request, event_id, compo_id):
    # Get compo
    compo = compo_times_formatter(get_object_or_404(Compo, pk=int(compo_id), active=True, event_id=int(event_id)))
    
    # Check if user may vote (voting open, user has code)
    can_vote = False
    if request.user.is_active and request.user.is_authenticated():
        try:
            vc = VoteCode.objects.get(associated_to=request.user, event_id=int(event_id))
            can_vote = True
        except VoteCode.DoesNotExist:
            pass
        
    # Handle entry adding
    if request.method == 'POST' and compo.is_adding_open():
        # Make sure user is authenticated
        if not request.user.is_active or not request.user.is_authenticated():
            raise Http403
        
        # Handle data
        entryform = EntryForm(request.POST, request.FILES, compo=compo)
        if entryform.is_valid():
            entry = entryform.save(commit=False)
            entry.user = request.user
            entry.compo = compo
            entry.save()
            return HttpResponseRedirect(reverse('kompomaatti-compo', args=(event_id, compo_id,)))
    else:
        entryform = EntryForm(compo=compo)
    
    # Get entries, and only show them if voting has started
    # (only show results if it has been allowed in model)
    all_entries = []
    if compo.has_voting_started:
        if compo.show_voting_results:
            all_entries = Entry.objects.filter(compo=compo)
        else:
            all_entries = Entry.objects.filter(compo=compo).order_by('name')
    
    # Get users entries
    my_entries = []
    if request.user.is_active and request.user.is_authenticated():
        my_entries = Entry.objects.filter(compo=compo, user=request.user)
    
    # Dump template
    return custom_render(request, 'kompomaatti/compo_details.html', {
        'sel_event_id': int(event_id),
        'compo': compo,
        'entryform': entryform,
        'can_vote': can_vote,
        'all_entries': all_entries,
        'my_entries': my_entries,
    })
    
@user_access_required
def compo_vote(request, event_id, compo_id):
    # Make sure the user has an active votecode
    try:
        vc = VoteCode.objects.get(associated_to=request.user, event_id=int(event_id))
    except VoteCode.DoesNotExist:
        raise Http403
    
    # Get compo
    compo = get_object_or_404(Compo, pk=int(compo_id))
    
    # Make sure voting is open
    if datetime.now() < compo.voting_start or datetime.now() > compo.voting_end:
        raise Http403
    
    # Get votes cast by user
    votes = Vote.objects.filter(user=request.user, compo=compo).order_by('rank')
    
    # Check if user has already voted
    has_voted = False
    if votes.count() > 0:
        has_voted = True
    
    # Get entries. If user hasn't voted yet, make sure the entries are in random order to minimize bias
    # If user has already voted, sort entries in previously voted order.
    nvoted_entries = []
    voted_entries = []
    if has_voted:
        # Get all entries
        nvoted_entries = Entry.objects.filter(compo=compo, disqualified=False).order_by('?')
        
        # Get voted entries. Add to "voted" list, remove from "not voted" list.
        for vote in votes:
            if not vote.entry.disqualified:
                voted_entries.append(vote.entry)
                nvoted_entries.remove(vote.entry)
    else:
        nvoted_entries = Entry.objects.filter(compo=compo).order_by('?')
    
    # Dump template
    return custom_render(request, 'kompomaatti/compo_vote.html', {
        'sel_event_id': int(event_id),
        'compo': compo,
        'voted_entries': voted_entries,
        'nvoted_entries': nvoted_entries,
        'has_voted': has_voted,
    })
    
@user_access_required
def compoentry_edit(request, event_id, compo_id, entry_id):
    # Get compo
    compo = get_object_or_404(Compo, pk=int(compo_id))
    
    # Check if user is allowed to edit
    if datetime.now() >= compo.editing_end:
        raise Http403
    
    # Get entry (make sure the user owns it, too)
    entry = get_object_or_404(Entry, pk=int(entry_id), compo=compo, user=request.user)
    
    # Handle entry adding
    if request.method == 'POST':
        entryform = EntryForm(request.POST, request.FILES, instance=entry, compo=compo)
        if entryform.is_valid():
            entryform.save()
            return HttpResponseRedirect(reverse('kompomaatti-compo', args=(event_id, compo_id,)))
    else:
        entryform = EntryForm(instance=entry, compo=compo)
    
    # Dump template
    return custom_render(request, 'kompomaatti/entry_edit.html', {
        'sel_event_id': int(event_id),
        'compo': compo,
        'entry': entry,
        'entryform': entryform,
    })
    
@user_access_required
def compoentry_delete(request, event_id, compo_id, entry_id):
    # Get compo
    compo = get_object_or_404(Compo, pk=int(compo_id))
    
    # Check if user is allowed to edit
    if datetime.now() >= compo.adding_end:
        raise Http403
    
    # Get entry (make sure the user owns it, too)
    entry = get_object_or_404(Entry, pk=int(entry_id), compo=compo, user=request.user)
    
    # Delete entry
    entry.delete()
    
    # Redirect
    return HttpResponseRedirect(reverse('kompomaatti-compo', args=(event_id, compo_id,)))
    
def competitions(request, event_id):
    # Get competitions
    competitions = []
    for competition in Competition.objects.filter(active=True, event_id=int(event_id)):
        competitions.append(competition_times_formatter(competition))
    
    # Dump the template
    return custom_render(request, 'kompomaatti/competitions.html', {
        'sel_event_id': int(event_id),
        'competitions': competitions,
    })
    
def competition_details(request, event_id, competition_id):
    # Get competition
    competition = competition_times_formatter(get_object_or_404(Competition, pk=int(competition_id), active=True, event_id=int(event_id)))
    
    # Check if user can participate (deadline not caught yet)
    can_participate = False
    if datetime.now() < competition.participation_end:
        can_participate = True
        
    # Handle signup form
    if request.method == 'POST' and can_participate:
        # Make sure user is authenticated
        if not request.user.is_active or not request.user.is_authenticated():
            raise Http403
        
        # Handle post data
        participationform = ParticipationForm(request.POST)
        if participationform.is_valid():
            p = participationform.save(commit=False)
            p.competition = competition
            p.user = request.user
            p.save()
            return HttpResponseRedirect(reverse('kompomaatti-competition', args=(event_id, competition_id,)))
    else:
        participationform = ParticipationForm()
    
    # Check if user has participated
    signed_up = False
    participation = None
    if request.user.is_active and request.user.is_authenticated():
        try:
            participation = CompetitionParticipation.objects.get(competition=competition, user=request.user)
            signed_up = True
        except CompetitionParticipation.DoesNotExist:
            pass
    
    # All done, dump template
    return custom_render(request, 'kompomaatti/competition_details.html', {
        'sel_event_id': int(event_id),
        'competition': competition,
        'participation': participation,
        'signed_up': signed_up,
        'can_participate': can_participate,
        'participationform': participationform,
    })

@user_access_required
def competition_signout(request, event_id, competition_id):
    # Get competition
    competition = get_object_or_404(Competition, pk=int(competition_id))
    
    # Check if user is still allowed to sign up
    if datetime.now() >= competition.participation_end:
        raise Http403
    
    # Delete participation
    try:
        CompetitionParticipation.objects.get(competition=competition, user=request.user).delete()
    except CompetitionParticipation.DoesNotExist:
        pass
    
    # Redirect
    return HttpResponseRedirect(reverse('kompomaatti-competition', args=(event_id, competition_id,)))

def entry_details(request, event_id, compo_id, entry_id):
    # Get compo
    compo = get_object_or_404(Compo, pk=int(compo_id))
    
    # Make sure voting has started before allowing this page to be shown
    if datetime.now() < compo.voting_start:
        raise Http404
    
    # Get entry
    entry = get_object_or_404(Entry, pk=int(entry_id), compo=compo)
    
    # Render
    return custom_render(request, 'kompomaatti/entry_details.html', {
        'sel_event_id': int(event_id),
        'entry': entry,
        'compo': compo,
    })

@user_access_required
def profile(request, event_id):
    # Get event
    event = get_object_or_404(Event, pk=int(event_id))
        
    # Check if user has the right to vote
    reserved_code = None
    can_vote = False
    try:
        votecode = VoteCode.objects.get(event=event, associated_to=request.user)
        reserved_code = votecode.key
        can_vote = True
    except VoteCode.DoesNotExist:
        pass
        
    # Check if request for vote code has been made
    request_made = False
    try:
        vcreq = VoteCodeRequest.objects.get(event=event, user=request.user)
        request_made = True
    except VoteCodeRequest.DoesNotExist:
        pass
        
    # Profile form
    if request.method == 'POST' and 'submit-profile' in request.POST:
        profileform = ProfileForm(request.POST, instance=request.user, user=request.user)
        if profileform.is_valid():
            profileform.save()
            return HttpResponseRedirect(reverse('kompomaatti-profile', args=(event_id,)))
    else:
        profileform = ProfileForm(instance=request.user, user=request.user)
    
    # Votecode Association form
    if request.method == 'POST' and 'submit-vcassoc' in request.POST:
        votecodeassocform = VoteCodeAssocForm(request.POST, event=event, user=request.user)
        if votecodeassocform.is_valid():
            votecodeassocform.save()
            return HttpResponseRedirect(reverse('kompomaatti-profile', args=(event_id,)))
    else:
        votecodeassocform = VoteCodeAssocForm(event=event, user=request.user)
    
    # Votecode Request form
    if request.method == 'POST' and 'submit-vcreq' in request.POST:
        votecoderequestform = VoteCodeRequestForm(request.POST)
        if votecoderequestform.is_valid():
            vcr = votecoderequestform.save(commit=False)
            vcr.user = request.user
            vcr.event = event
            vcr.save()
            return HttpResponseRedirect(reverse('kompomaatti-profile', args=(event_id,)))
    else:
        votecoderequestform = VoteCodeRequestForm()
    
    # Render
    return custom_render(request, 'kompomaatti/profile.html', {
        'sel_event_id': int(event_id),
        'profileform': profileform,
        'votecodeassocform': votecodeassocform,
        'votecoderequestform': votecoderequestform,
        'reserved_code': reserved_code,
        'can_vote': can_vote,
        'request_made': request_made,
    })
    
def do_login(request, event_id):
    loginform = OpenIDLoginForm(next=reverse('kompomaatti-index', args=(event_id,)))
    
    return custom_render(request, 'kompomaatti/login.html', {
        'sel_event_id': int(event_id),
        'openidform': loginform,
    })
    
@user_access_required
def do_logout(request, event_id):
    logout(request)
    return HttpResponseRedirect(reverse('kompomaatti-index', args=(event_id,)))

