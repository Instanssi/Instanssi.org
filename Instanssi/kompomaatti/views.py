# -*- coding: utf-8 -*-

from Instanssi.common.http import Http403
from Instanssi.common.auth import user_access_required
from Instanssi.common.rest import rest_api, RestResponse

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.utils import timezone

from Instanssi.kompomaatti.forms import VoteCodeRequestForm, ParticipationForm,\
    EntryForm, TicketVoteCodeAssocForm
from Instanssi.kompomaatti.models import Event, VoteCodeRequest, TicketVoteCode, Compo, Entry,\
    Vote, CompetitionParticipation, Competition, Profile, VoteGroup
from Instanssi.kompomaatti.misc.time_formatting import compo_times_formatter, competition_times_formatter
from Instanssi.kompomaatti.misc import awesometime, entrysort
from Instanssi.kompomaatti.misc.events import get_upcoming
from Instanssi.store.models import TransactionItem


def eventselect(request):
    try:
        latest_event = Event.objects.latest('id')
    except Event.DoesNotExist:
        return render(request, 'kompomaatti/event_select.html', {})

    return HttpResponseRedirect(reverse('km:index', args=(latest_event.pk,)))


def index(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    
    # Add urls and formatted timestamps to event list
    events = []
    for event in get_upcoming(event):
        event['formatted_time'] = awesometime.format_single(event['date'])
        if event['type'] == 1:
            event['url'] = reverse('km:compo', args=(event_id, event['id'],))
        elif event['type'] == 2:
            event['url'] = reverse('km:competition', args=(event_id, event['id'],))
        else:
            event['url'] = None
    
        # Add to list
        events.append(event)
    
    # Check if user has an associated vote code
    votecode_associated = False
    if request.user.is_authenticated:
        # See if ticket is used as votecode
        try:
            TicketVoteCode.objects.get(event=event_id, associated_to=request.user)
            votecode_associated = True
        except TicketVoteCode.DoesNotExist:
            pass
        # See if votecode request is accepted
        try:
            VoteCodeRequest.objects.get(event=event_id, user=request.user, status=1)
            votecode_associated = True
        except VoteCodeRequest.DoesNotExist:
            pass
    else:
        votecode_associated = True

    # Get compos the user has not yet voted on
    not_voted_on = []
    if request.user.is_active and request.user.is_authenticated and votecode_associated:
        for compo in Compo.objects.filter(event=event_id, active=True):
            if compo.is_voting_open():
                if Vote.objects.filter(user=request.user, compo=compo).count() == 0:
                    not_voted_on.append(compo)

    # Has profile already been checked and saved
    profile_checked = False
    if request.user.is_authenticated and Profile.objects.filter(user=request.user).exists():
        profile_checked = True

    # All done, dump template
    return render(request, 'kompomaatti/index.html', {
        'sel_event_id': int(event_id),
        'events': events,
        'not_voted_on': not_voted_on,
        'votecode_associated': votecode_associated,
        'profile_checked': profile_checked
    })


def compos(request, event_id):
    # Get compos, format times
    compo_list = []
    for compo in Compo.objects.filter(active=True, event_id=int(event_id)):
        compo_list.append(compo_times_formatter(compo))
    
    # Dump the template
    return render(request, 'kompomaatti/compos.html', {
        'sel_event_id': int(event_id),
        'compos': compo_list,
    })


def compo_details(request, event_id, compo_id):
    # Get compo
    compo = compo_times_formatter(get_object_or_404(Compo, pk=compo_id, active=True, event=event_id))
    
    # Check if user may vote (voting open, user has code)
    can_vote = False
    if request.user.is_active and request.user.is_authenticated:
        # See if ticket is used as votecode
        try:
            TicketVoteCode.objects.get(associated_to=request.user, event=event_id)
            can_vote = True
        except TicketVoteCode.DoesNotExist:
            pass

        if not can_vote:
            try:
                VoteCodeRequest.objects.get(user=request.user, event=event_id, status=1)
                can_vote = True
            except VoteCodeRequest.DoesNotExist:
                pass

    # Handle entry adding
    if request.method == 'POST' and compo.is_adding_open():
        # Make sure user is authenticated
        if not request.user.is_active or not request.user.is_authenticated:
            raise Http403
        
        # Handle data
        entryform = EntryForm(request.POST, request.FILES, compo=compo)
        if entryform.is_valid():
            entry = entryform.save(commit=False)
            entry.user = request.user
            entry.compo = compo
            entry.save()
            return HttpResponseRedirect(reverse('km:compo', args=(event_id, compo_id,)))
    else:
        entryform = EntryForm(compo=compo)
    
    # Get entries, and only show them if voting has started
    # (only show results if it has been allowed in model)
    all_entries = []
    if compo.has_voting_started:
        if compo.show_voting_results:
            all_entries = entrysort.sort_by_score(Entry.objects.filter(compo=compo))
        else:
            all_entries = Entry.objects.filter(compo=compo).order_by('name')
    
    # Stuff for users that have logged in 
    my_entries = []
    has_voted = False
    if request.user.is_active and request.user.is_authenticated:
        # Get all entries added by the user
        my_entries = Entry.objects.filter(compo=compo, user=request.user)
    
        # Check if user has already voted
        if Vote.objects.filter(user=request.user, compo=compo).count() > 0:
            has_voted = True
    
    # Dump template
    return render(request, 'kompomaatti/compo_details.html', {
        'sel_event_id': int(event_id),
        'compo': compo,
        'entryform': entryform,
        'can_vote': can_vote,
        'all_entries': all_entries,
        'my_entries': my_entries,
        'has_voted': has_voted,
    })


@user_access_required
def compo_vote(request, event_id, compo_id):
    # Make sure the user has an active votecode or ticket votecode
    can_vote = False
    try:
        TicketVoteCode.objects.get(associated_to=request.user, event=event_id)
        can_vote = True
    except TicketVoteCode.DoesNotExist:
        pass

    if not can_vote:
        try:
            VoteCodeRequest.objects.get(user=request.user, event=event_id, status=1)
            can_vote = True
        except VoteCodeRequest.DoesNotExist:
            pass

    if not can_vote:
        raise Http403

    # Get compo
    compo = get_object_or_404(Compo, pk=int(compo_id))
    
    # Make sure voting is open
    if not compo.is_voting_open():
        raise Http403
    
    # Get votes cast by user
    votes = Vote.objects.filter(user=request.user, compo=compo).order_by('rank')
    
    # Check if user has already voted
    has_voted = False
    if votes.count() > 0:
        has_voted = True
    
    # Check if we have data!
    if request.method == 'POST':
        # Get as list, convert to ints
        results = []
        _results = request.POST.getlist('results[]')
        for result in _results:
            results.append(int(result))
        
        # Make sure we have right amount of entries (more than 0)
        if len(results) < 1:
            return HttpResponse("On äänestettävä vähintään yhtä entryä.")
        
        # Make sure there are no id's twice
        _checked = []
        for id in results:
            if id in _checked:
                return HttpResponse("Syötevirhe!")
            else:
                _checked.append(id)

        # See that all id's are entries belonging to this compo
        entries = []
        try:
            for entry_id in results:
                entry = Entry.objects.get(compo=compo, disqualified=False, id=entry_id)
                entries.append(entry)
        except Entry.DoesNotExist:
            return HttpResponse("Syötevirhe")

        # Delete old entries (if any) and add new ones
        group = VoteGroup.objects.filter(compo=compo, user=request.user).first()
        if group:
            group.delete_votes()
        else:
            group = VoteGroup.objects.create(
                user=request.user,
                compo=compo
            )

        # Add new voted entries
        group.create_votes(entries)
        
        # Return success message
        return HttpResponse("0")
    
    # Get entries. If user hasn't voted yet, make sure the entries are in random order to minimize bias
    # If user has already voted, sort entries in previously voted order.
    nvoted_entries = []
    voted_entries = []
    if has_voted:
        # Get voted entries. Add to "voted" list
        for vote in votes:
            if not vote.entry.disqualified:
                voted_entries.append(vote.entry)
                
        # Get all entries
        _nvoted_entries = Entry.objects.filter(compo=compo, disqualified=False).order_by('?')
        for entry in _nvoted_entries:
            if entry not in voted_entries:
                nvoted_entries.append(entry)
    else:
        nvoted_entries = Entry.objects.filter(compo=compo, disqualified=False).order_by('?')
    
    # Dump template
    return render(request, 'kompomaatti/compo_vote.html', {
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
    if timezone.now() >= compo.editing_end:
        raise Http403
    
    # Get entry (make sure the user owns it, too)
    entry = get_object_or_404(Entry, pk=int(entry_id), compo=compo, user=request.user)
    
    # Handle entry adding
    if request.method == 'POST':
        entryform = EntryForm(request.POST, request.FILES, instance=entry, compo=compo)
        if entryform.is_valid():
            entryform.save()
            return HttpResponseRedirect(reverse('km:compo', args=(event_id, compo_id,)))
    else:
        entryform = EntryForm(instance=entry, compo=compo)
    
    # Dump template
    return render(request, 'kompomaatti/entry_edit.html', {
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
    if timezone.now() >= compo.adding_end:
        raise Http403
    
    # Get entry (make sure the user owns it, too)
    entry = get_object_or_404(Entry, pk=int(entry_id), compo=compo, user=request.user)
    
    # Delete entry
    entry.delete()
    
    # Redirect
    return HttpResponseRedirect(reverse('km:compo', args=(event_id, compo_id,)))


def competitions(request, event_id):
    # Get competitions
    competitions = []
    for competition in Competition.objects.filter(active=True, event_id=int(event_id)):
        competitions.append(competition_times_formatter(competition))
    
    # Dump the template
    return render(request, 'kompomaatti/competitions.html', {
        'sel_event_id': int(event_id),
        'competitions': competitions,
    })


def competition_details(request, event_id, competition_id):
    # Get competition
    competition = competition_times_formatter(get_object_or_404(Competition, pk=int(competition_id), active=True, event_id=int(event_id)))
    
    # Check if user can participate (deadline not caught yet)
    can_participate = False
    if timezone.now() < competition.participation_end:
        can_participate = True
        
    # Handle signup form
    if request.method == 'POST' and can_participate:
        # Make sure user is authenticated
        if not request.user.is_active or not request.user.is_authenticated:
            raise Http403
        
        # Handle post data
        participationform = ParticipationForm(request.POST)
        if participationform.is_valid():
            p = participationform.save(commit=False)
            p.competition = competition
            p.user = request.user
            p.save()
            return HttpResponseRedirect(reverse('km:competition', args=(event_id, competition_id,)))
    else:
        participationform = ParticipationForm()
    
    # Get all participants
    participants = CompetitionParticipation.objects.filter(competition=competition)
    
    # Check if user has participated
    signed_up = False
    participation = None
    if request.user.is_active and request.user.is_authenticated:
        try:
            participation = CompetitionParticipation.objects.get(competition=competition, user=request.user)
            signed_up = True
        except CompetitionParticipation.DoesNotExist:
            pass
    
    # All done, dump template
    return render(request, 'kompomaatti/competition_details.html', {
        'sel_event_id': int(event_id),
        'competition': competition,
        'participation': participation,
        'signed_up': signed_up,
        'can_participate': can_participate,
        'participationform': participationform,
        'participants': participants,
    })


@user_access_required
def competition_signout(request, event_id, competition_id):
    # Get competition
    competition = get_object_or_404(Competition, pk=int(competition_id))
    
    # Check if user is still allowed to sign up
    if timezone.now() >= competition.participation_end:
        raise Http403
    
    # Delete participation
    try:
        CompetitionParticipation.objects.get(competition=competition, user=request.user).delete()
    except CompetitionParticipation.DoesNotExist:
        pass
    
    # Redirect
    return HttpResponseRedirect(reverse('km:competition', args=(event_id, competition_id,)))


def entry_details(request, event_id, compo_id, entry_id):
    # Get compo
    compo = get_object_or_404(Compo, pk=int(compo_id))
    
    # Make sure voting has started before allowing this page to be shown
    if timezone.now() < compo.voting_start:
        raise Http404
    
    # Get entry
    entry = get_object_or_404(Entry, pk=int(entry_id), compo=compo)
    
    # Render
    return render(request, 'kompomaatti/entry_details.html', {
        'sel_event_id': int(event_id),
        'entry': entry,
        'compo': compo,
    })


@user_access_required
@rest_api
def validate_votecode_api(request, event_id, vote_code):
    event = get_object_or_404(Event, pk=event_id)

    # Make sure the key length is at least 8 chars before doing anything
    if len(vote_code) < 8:
        return RestResponse(code=403, error_text='Lippuavain liian lyhyt!')

    # Check if key is already used, return error if it is
    try:
        TicketVoteCode.objects.get(event=event, ticket__key__startswith=vote_code)
        return RestResponse(code=403, error_text='Lippuavain on jo käytössä!')
    except TicketVoteCode.DoesNotExist:
        pass

    # Check if key exists
    try:
        TransactionItem.objects.get(item__event=event, item__is_ticket=True, key__startswith=vote_code)
    except TransactionItem.DoesNotExist:
        return RestResponse(code=403, error_text='Lippuavainta ei ole olemassa!')

    # Everything done. Return default response with code 200 and no error text.
    return RestResponse({})


@user_access_required
def votecode(request, event_id):
    # Get event
    event = get_object_or_404(Event, pk=int(event_id))
        
    # Check if user has the right to vote via separate vote code
    reserved_code = None
    can_vote = False
    votecode_type = None

    # Check if user has the right to vote via ticket
    try:
        ticket_votecode = TicketVoteCode.objects.get(event=event, associated_to=request.user)
        reserved_code = ticket_votecode.ticket.key
        can_vote = True
        votecode_type = "ticket"
    except TicketVoteCode.DoesNotExist:
        pass

    # Check if request for vote code has been made
    request_made = False
    request_failed = False
    try:
        vcr = VoteCodeRequest.objects.get(event=event, user=request.user)
        if vcr.status == 0:
            request_made = True
        elif vcr.status == 1:
            can_vote = True
            votecode_type = 'request'
        else:
            request_failed = True
    except VoteCodeRequest.DoesNotExist:
        pass

    # Ticket votecode association form
    if request.method == 'POST' and 'submit-ticketvcassoc' in request.POST:
        ticket_votecode_form = TicketVoteCodeAssocForm(request.POST, event=event, user=request.user)
        if ticket_votecode_form.is_valid():
            ticket_votecode_form.save()
            return HttpResponseRedirect(reverse('km:votecode', args=(event_id,)))
    else:
        ticket_votecode_form = TicketVoteCodeAssocForm(event=event, user=request.user)
    
    # Votecode Request form
    if request.method == 'POST' and 'submit-vcreq' in request.POST:
        votecoderequestform = VoteCodeRequestForm(request.POST)
        if votecoderequestform.is_valid():
            vcr = votecoderequestform.save(commit=False)
            vcr.user = request.user
            vcr.event = event
            vcr.save()
            return HttpResponseRedirect(reverse('km:votecode', args=(event_id,)))
    else:
        votecoderequestform = VoteCodeRequestForm()
    
    # Render
    return render(request, 'kompomaatti/votecode.html', {
        'sel_event_id': int(event_id),
        'votecoderequestform': votecoderequestform,
        'ticket_votecode_form': ticket_votecode_form,
        'reserved_code': reserved_code,
        'can_vote': can_vote,
        'votecode_type': votecode_type,
        'request_made': request_made,
        'request_failed': request_failed
    })

