# -*- coding: utf-8 -*-

import logging

from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.template import loader

from Instanssi.kompomaatti.models import VoteCodeRequest, TicketVoteCode, Compo, Event, Entry, Competition,\
    CompetitionParticipation
from Instanssi.admin_kompomaatti.forms import AdminCompoForm, AdminCompetitionForm, AdminCompetitionScoreForm,\
    AdminEntryAddForm, AdminEntryEditForm, AdminParticipationEditForm, CloneCompoForm
from Instanssi.kompomaatti.misc import entrysort
from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.common.http import Http403
from Instanssi.common.auth import staff_access_required
from Instanssi.kompomaatti import tasks

logger = logging.getLogger(__name__)


@staff_access_required
def index(request, sel_event_id):
    # Render response
    return admin_render(request, "admin_kompomaatti/index.html", {
        'selected_event_id': int(sel_event_id),
    })


@staff_access_required
def entries_csv(request, sel_event_id):
    entries = []

    # Get event
    event = get_object_or_404(Event, pk=sel_event_id)

    # Find all compos and their top 3 entries
    compos = Compo.objects.filter(event=event)

    # Get the entries
    for compo in compos:
        compo_results = entrysort.sort_by_score(Entry.objects.filter(compo=compo))
        if len(compo_results) > 3:
            entries = entries + compo_results[:3]
        else:
            entries = entries + compo_results

    # Placements, copypasta
    for entry in entries:
        m = entry.get_rank()
        if m == 1:
            entry.placement = 'I'
        if m == 2:
            entry.placement = 'II'
        if m == 3:
            entry.placement = 'III'

    # Respond with entries CSV (text/csv)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="instanssi_entries.csv"'
    t = loader.get_template('admin_kompomaatti/entries_csv.txt')
    response.write(t.render({
        'entries': entries,
    }))
    return response


@staff_access_required
def competition_score(request, sel_event_id, competition_id):
    # Get competition
    competition = get_object_or_404(Competition, pk=competition_id)
    
    # Handle form
    if request.method == 'POST':
        # Check permissions
        if not request.user.has_perm('kompomaatti.change_competitionparticipation'):
            raise Http403
        
        # Handle form
        scoreform = AdminCompetitionScoreForm(request.POST, competition=competition)
        if scoreform.is_valid():
            scoreform.save()
            logger.info('Competition scores set.', extra={'user': request.user, 'event_id': sel_event_id})
            return HttpResponseRedirect(reverse('manage-kompomaatti:competitions', args=(sel_event_id,))) 
    else:
        scoreform = AdminCompetitionScoreForm(competition=competition)
    
    # Render response
    return admin_render(request, "admin_kompomaatti/competition_score.html", {
        'competition': competition,
        'scoreform': scoreform,
        'selected_event_id': int(sel_event_id),
    })


@staff_access_required
def competition_participations(request, sel_event_id, competition_id):
    # Get competition
    participants = CompetitionParticipation.objects.filter(competition_id=int(competition_id))
    
    # Render response
    return admin_render(request, "admin_kompomaatti/competition_participations.html", {
        'participants': participants,
        'selected_event_id': int(sel_event_id),
    })


@staff_access_required
def competition_participation_edit(request, sel_event_id, competition_id, pid):
    # CHeck for permissions
    if not request.user.has_perm('kompomaatti.change_competitionparticipation'):
        raise Http403
    
    # Get competition, participation
    competition = get_object_or_404(Competition, pk=int(competition_id))
    participant = get_object_or_404(CompetitionParticipation, pk=int(pid))
    
    # Handle form
    if request.method == 'POST':
        pform = AdminParticipationEditForm(request.POST, instance=participant)
        if pform.is_valid():
            pform.save()
            logger.info('Competition participation information edited.',
                        extra={'user': request.user, 'event_id': sel_event_id})
            return HttpResponseRedirect(reverse('manage-kompomaatti:participations',
                                                args=(sel_event_id, competition_id,)))
    else:
        pform = AdminParticipationEditForm(instance=participant)
    
    # Render response
    return admin_render(request, "admin_kompomaatti/participation_edit.html", {
        'pform': pform,
        'selected_event_id': int(sel_event_id),
        'competition': competition,
    })
    
    
@staff_access_required
def competitions_browse(request, sel_event_id):
    # Get competitions
    competitions = Competition.objects.filter(event_id=int(sel_event_id))
    
    # Form handling
    if request.method == "POST":
        # CHeck for permissions
        if not request.user.has_perm('kompomaatti.add_competition'):
            raise Http403
        
        # Handle form
        competitionform = AdminCompetitionForm(request.POST)
        if competitionform.is_valid():
            data = competitionform.save(commit=False)
            data.event_id = int(sel_event_id)
            data.save()
            logger.info('Competition "{}" added.'.format(data.name),
                        extra={'user': request.user, 'event_id': sel_event_id})
            return HttpResponseRedirect(reverse('manage-kompomaatti:competitions', args=(sel_event_id,))) 
    else:
        competitionform = AdminCompetitionForm()
    
    # Render response
    return admin_render(request, "admin_kompomaatti/competitions.html", {
        'competitions': competitions,
        'competitionform': competitionform,
        'selected_event_id': int(sel_event_id),
    })


@staff_access_required
def competition_edit(request, sel_event_id, competition_id):
    # CHeck for permissions
    if not request.user.has_perm('kompomaatti.change_competition'):
        raise Http403
    
    # Get competition
    competition = get_object_or_404(Competition, pk=competition_id)
    
    # Handle form
    if request.method == "POST":
        competitionform = AdminCompetitionForm(request.POST, instance=competition)
        if competitionform.is_valid():
            c = competitionform.save()
            logger.info('Competition "{}" edited.'.format(c.name),
                        extra={'user': request.user, 'event_id': sel_event_id})
            return HttpResponseRedirect(reverse('manage-kompomaatti:competitions', args=(sel_event_id,))) 
    else:
        competitionform = AdminCompetitionForm(instance=competition)
    
    # Render response
    return admin_render(request, "admin_kompomaatti/competition_edit.html", {
        'competition': competition,
        'competitionform': competitionform,
        'selected_event_id': int(sel_event_id),
    })


@staff_access_required
def competition_delete(request, sel_event_id, competition_id):
    # CHeck for permissions
    if not request.user.has_perm('kompomaatti.delete_competition'):
        raise Http403
    
    # Delete competition
    try:
        c = Competition.objects.get(pk=competition_id)
        c.delete()
        logger.info('Competition "{}" deleted.'.format(c.name),
                    extra={'user': request.user, 'event_id': sel_event_id})
    except Competition.DoesNotExist:
        pass
    
    # Redirect
    return HttpResponseRedirect(reverse('manage-kompomaatti:competitions', args=(sel_event_id,))) 


@staff_access_required
def compo_browse(request, sel_event_id):
    # Get compos
    compos = Compo.objects.filter(event_id=int(sel_event_id))

    if request.method == "POST" and 'submit-clone' in request.POST:
        if not request.user.has_perm('kompomaatti.add_compo'):
            raise Http403

        clonecompoform = CloneCompoForm(request.POST)
        if clonecompoform.is_valid():
            clonecompoform.save(event_id=sel_event_id)
            logger.info('Compos from other event cloned.',
                        extra={'user': request.user, 'event_id': sel_event_id})
            return HttpResponseRedirect(reverse('manage-kompomaatti:compos', args=(sel_event_id,)))
    else:
        clonecompoform = CloneCompoForm()

    # Form handling
    if request.method == "POST" and 'submit-compo' in request.POST:
        # CHeck for permissions
        if not request.user.has_perm('kompomaatti.add_compo'):
            raise Http403
        
        # Handle form
        compoform = AdminCompoForm(request.POST)
        if compoform.is_valid():
            data = compoform.save(commit=False)
            data.event_id = int(sel_event_id)
            data.save()
            logger.info('Compo "{}" added.'.format(data.name),
                        extra={'user': request.user, 'event_id': sel_event_id})
            return HttpResponseRedirect(reverse('manage-kompomaatti:compos', args=(sel_event_id,))) 
    else:
        compoform = AdminCompoForm()
    
    # Render response
    return admin_render(request, "admin_kompomaatti/compo_browse.html", {
        'compos': compos,
        'compoform': compoform,
        'clonecompoform': clonecompoform,
        'selected_event_id': int(sel_event_id),
    })


@staff_access_required
def compo_edit(request, sel_event_id, compo_id):
    # CHeck for permissions
    if not request.user.has_perm('kompomaatti.change_compo'):
        raise Http403
    
    # Get compo
    compo = get_object_or_404(Compo, pk=compo_id)
    
    # Handle form
    if request.method == "POST":
        editform = AdminCompoForm(request.POST, instance=compo)
        if editform.is_valid():
            c = editform.save()
            logger.info('Compo "{}" edited.'.format(c.name),
                        extra={'user': request.user, 'event_id': sel_event_id})
            return HttpResponseRedirect(reverse('manage-kompomaatti:compos', args=(sel_event_id,))) 
    else:
        editform = AdminCompoForm(instance=compo)
    
    # Render response
    return admin_render(request, "admin_kompomaatti/compo_edit.html", {
        'compo': compo,
        'editform': editform,
        'selected_event_id': int(sel_event_id),
    })


@staff_access_required
def compo_delete(request, sel_event_id, compo_id):
    # CHeck for permissions
    if not request.user.has_perm('kompomaatti.delete_compo'):
        raise Http403
    
    # Delete competition
    try:
        c = Compo.objects.get(pk=compo_id)
        c.delete()
        logger.info('Compo "{}" deleted.'.format(c.name),
                    extra={'user': request.user, 'event_id': sel_event_id})
    except Compo.DoesNotExist:
        pass
    
    # Redirect
    return HttpResponseRedirect(reverse('manage-kompomaatti:compos', args=(sel_event_id,))) 


@staff_access_required
def entry_browse(request, sel_event_id):
    # Get event
    event = get_object_or_404(Event, pk=sel_event_id)
    
    # Form handling
    if request.method == "POST":
        # CHeck for permissions
        if not request.user.has_perm('kompomaatti.add_entry'):
            raise Http403
        
        # Handle form
        entryform = AdminEntryAddForm(request.POST, request.FILES, event=event)
        if entryform.is_valid():
            e = entryform.save()
            logger.info('Compo entry "{}" added.'.format(e.name),
                        extra={'user': request.user, 'event_id': sel_event_id})
            return HttpResponseRedirect(reverse('manage-kompomaatti:entries', args=(sel_event_id,))) 
    else:
        entryform = AdminEntryAddForm(event=event)
    
    # Get Entries    
    compos = Compo.objects.filter(event=int(sel_event_id))
    entries = Entry.objects.filter(compo__in=compos)
    
    # Render response
    return admin_render(request, "admin_kompomaatti/entry_browse.html", {
        'entries': entries,
        'entryform': entryform,
        'selected_event_id': int(sel_event_id),
    })


@staff_access_required
def entry_edit(request, sel_event_id, entry_id):
    # CHeck for permissions
    if not request.user.has_perm('kompomaatti.change_entry'):
        raise Http403
    
    # Check ID
    entry = get_object_or_404(Entry, pk=entry_id)
    
    # Get event
    event = get_object_or_404(Event, pk=sel_event_id)
    
    # Handle form
    if request.method == "POST":
        editform = AdminEntryEditForm(request.POST, request.FILES, instance=entry, event=event)
        if editform.is_valid():
            e = editform.save()
            logger.info('Compo entry "{}" edited.'.format(e.name),
                        extra={'user': request.user, 'event_id': sel_event_id})
            return HttpResponseRedirect(reverse('manage-kompomaatti:entries', args=(sel_event_id,))) 
    else:
        editform = AdminEntryEditForm(instance=entry, event=event)
    
    # Render response
    return admin_render(request, "admin_kompomaatti/entry_edit.html", {
        'entry': entry,
        'editform': editform,
        'selected_event_id': int(sel_event_id),
    })


@staff_access_required
def entry_delete(request, sel_event_id, entry_id):
    # CHeck for permissions
    if not request.user.has_perm('kompomaatti.delete_entry'):
        raise Http403
    
    # Get entry
    entry = get_object_or_404(Entry, pk=entry_id)
    
    # Delete entry
    entry.entryfile.delete()
    if entry.sourcefile:
        entry.sourcefile.delete()
    if entry.imagefile_original:
        entry.imagefile_original.delete()
    entry.delete()
    logger.info('Compo entry "{}" deleted.'.format(entry.name),
                extra={'user': request.user, 'event_id': sel_event_id})

    # Redirect
    return HttpResponseRedirect(reverse('manage-kompomaatti:entries', args=(sel_event_id,))) 


@staff_access_required
def generate_result_package(request, sel_event_id, compo_id):
    tasks.rebuild_collection.delay(compo_id)
    return HttpResponseRedirect(reverse('manage-kompomaatti:results', args=(sel_event_id,)))


@staff_access_required
def results(request, sel_event_id):
    # Get compos. competitions
    compos = Compo.objects.filter(event_id=int(sel_event_id))
    competitions = Competition.objects.filter(event_id=int(sel_event_id))

    # Get the entries
    compo_results = {}
    for compo in compos:
        compo_results[compo] = entrysort.sort_by_score(Entry.objects.filter(compo=compo))
    
    # Get competition participations
    competition_results = {}
    for competition in competitions:
        rankby = '-score'
        if competition.score_sort == 1:
            rankby = 'score'
        competition_results[competition.name] = \
            CompetitionParticipation.objects.filter(competition=competition).order_by(rankby)
    
    # Render response
    return admin_render(request, "admin_kompomaatti/results.html", {
        'compo_results': compo_results,
        'competition_results': competition_results,
        'selected_event_id': int(sel_event_id),
    })


@staff_access_required
def ticket_votecodes(request, sel_event_id):
    # Get tokens
    tokens = TicketVoteCode.objects.filter(event_id=sel_event_id)

    # Render response
    return admin_render(request, "admin_kompomaatti/ticketvotecodes.html", {
        'tokens': tokens,
        'selected_event_id': int(sel_event_id),
    })


@staff_access_required
def votecoderequests(request, sel_event_id):
    # Get all requests
    requests = VoteCodeRequest.objects.filter(event_id=int(sel_event_id,))
    
    # Render response
    return admin_render(request, "admin_kompomaatti/vcrequests.html", {
        'requests': requests,
        'selected_event_id': int(sel_event_id),
    })


@staff_access_required
def votecoderequests_accept(request, sel_event_id, vcrid):
    # CHeck for permissions
    if not request.user.has_perm('kompomaatti.change_votecode'):
        raise Http403

    # Get the request and change status to accepted
    vcr = get_object_or_404(VoteCodeRequest, pk=vcrid)
    logger.info('Votecode request from "{}" accepted.'.format(vcr.user.username),
                extra={'user': request.user, 'event_id': sel_event_id})
    vcr.status = 1
    vcr.save()

    # Return to admin page
    return HttpResponseRedirect(reverse('manage-kompomaatti:votecoderequests', args=(sel_event_id,))) 


@staff_access_required
def votecoderequests_reject(request, sel_event_id, vcrid):
    # CHeck for permissions
    if not request.user.has_perm('kompomaatti.change_votecode'):
        raise Http403

    # Get the request and change status to accepted
    vcr = get_object_or_404(VoteCodeRequest, pk=vcrid)
    logger.info('Votecode request from "{}" rejected.'.format(vcr.user.username),
                extra={'user': request.user, 'event_id': sel_event_id})
    vcr.status = 2
    vcr.save()

    # Return to admin page
    return HttpResponseRedirect(reverse('manage-kompomaatti:votecoderequests', args=(sel_event_id,)))
