import csv
import logging

from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse

from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.admin_kompomaatti.forms import (
    AdminCompetitionForm,
    AdminCompetitionScoreForm,
    AdminCompoForm,
    AdminEntryAddForm,
    AdminEntryEditForm,
    AdminParticipationEditForm,
    CloneCompoForm,
)
from Instanssi.common.auth import staff_access_required
from Instanssi.kompomaatti import tasks
from Instanssi.kompomaatti.misc import entrysort
from Instanssi.kompomaatti.models import (
    Competition,
    CompetitionParticipation,
    Compo,
    Entry,
    Event,
    TicketVoteCode,
    VoteCodeRequest,
)

logger = logging.getLogger(__name__)


@staff_access_required
def index(request: HttpRequest, selected_event_id: int) -> HttpResponse:
    return admin_render(request, "admin_kompomaatti/index.html", {"selected_event_id": selected_event_id})


@staff_access_required
def entries_csv(request: HttpRequest, selected_event_id: int) -> HttpResponse:
    event = get_object_or_404(Event, pk=selected_event_id)
    compos = Compo.objects.filter(event=event)
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="instanssi_entries.csv"'},
    )

    # Write data directly to the response via the CSV writer
    writer = csv.writer(response, dialect="unix")
    for compo in compos:
        for entry in entrysort.sort_by_score(Entry.objects.filter(compo=compo))[:3]:
            m = entry.get_rank()
            placement = "I" * m
            writer.writerow([entry.name, entry.creator, placement, entry.compo.name])

    return response


@staff_access_required
def competition_score(request: HttpRequest, selected_event_id: int, competition_id: int) -> HttpResponse:
    competition = get_object_or_404(Competition, pk=competition_id)

    if request.method == "POST":
        if not request.user.has_perm("kompomaatti.change_competitionparticipation"):
            raise PermissionDenied()

        score_form = AdminCompetitionScoreForm(request.POST, competition=competition)
        if score_form.is_valid():
            score_form.save()
            logger.info(
                "Competition scores set", extra={"user": request.user, "event_id": selected_event_id}
            )
            return HttpResponseRedirect(
                reverse("manage-kompomaatti:competitions", args=(selected_event_id,))
            )
    else:
        score_form = AdminCompetitionScoreForm(competition=competition)

    # Render response
    return admin_render(
        request,
        "admin_kompomaatti/competition_score.html",
        {"competition": competition, "scoreform": score_form, "selected_event_id": selected_event_id},
    )


@staff_access_required
def competition_participations(
    request: HttpRequest, selected_event_id: int, competition_id: int
) -> HttpResponse:
    participants = CompetitionParticipation.objects.filter(competition_id=competition_id)
    return admin_render(
        request,
        "admin_kompomaatti/competition_participations.html",
        {"participants": participants, "selected_event_id": selected_event_id},
    )


@staff_access_required
@permission_required("kompomaatti.change_competitionparticipation", raise_exception=True)
def competition_participation_edit(
    request: HttpRequest, selected_event_id: int, competition_id: int, participation_id: int
) -> HttpResponse:
    competition = get_object_or_404(Competition, pk=competition_id)
    participant = get_object_or_404(CompetitionParticipation, pk=participation_id)

    if request.method == "POST":
        participation_form = AdminParticipationEditForm(request.POST, instance=participant)
        if participation_form.is_valid():
            participation_form.save()
            logger.info(
                "Competition participation information edited",
                extra={"user": request.user, "event_id": selected_event_id},
            )
            return HttpResponseRedirect(
                reverse("manage-kompomaatti:participations", args=(selected_event_id, competition_id))
            )
    else:
        participation_form = AdminParticipationEditForm(instance=participant)

    return admin_render(
        request,
        "admin_kompomaatti/participation_edit.html",
        {"pform": participation_form, "selected_event_id": selected_event_id, "competition": competition},
    )


@staff_access_required
def competitions_browse(request: HttpRequest, selected_event_id: int) -> HttpResponse:
    competitions = Competition.objects.filter(event_id=selected_event_id)

    if request.method == "POST":
        if not request.user.has_perm("kompomaatti.add_competition"):
            raise PermissionDenied()

        competition_form = AdminCompetitionForm(request.POST)
        if competition_form.is_valid():
            data = competition_form.save(commit=False)
            data.event_id = selected_event_id
            data.save()
            logger.info(
                "Competition '%s' added.",
                data.name,
                extra={"user": request.user, "event_id": selected_event_id},
            )
            return HttpResponseRedirect(
                reverse("manage-kompomaatti:competitions", args=(selected_event_id,))
            )
    else:
        competition_form = AdminCompetitionForm()

    return admin_render(
        request,
        "admin_kompomaatti/competitions.html",
        {
            "competitions": competitions,
            "competitionform": competition_form,
            "selected_event_id": selected_event_id,
        },
    )


@staff_access_required
@permission_required("kompomaatti.change_competition", raise_exception=True)
def competition_edit(request: HttpRequest, selected_event_id: int, competition_id: int) -> HttpResponse:
    competition = get_object_or_404(Competition, pk=competition_id)

    if request.method == "POST":
        competition_form = AdminCompetitionForm(request.POST, instance=competition)
        if competition_form.is_valid():
            c = competition_form.save()
            logger.info(
                "Competition '%s' edited",
                c.name,
                extra={"user": request.user, "event_id": selected_event_id},
            )
            return HttpResponseRedirect(
                reverse("manage-kompomaatti:competitions", args=(selected_event_id,))
            )
    else:
        competition_form = AdminCompetitionForm(instance=competition)

    return admin_render(
        request,
        "admin_kompomaatti/competition_edit.html",
        {
            "competition": competition,
            "competitionform": competition_form,
            "selected_event_id": selected_event_id,
        },
    )


@staff_access_required
@permission_required("kompomaatti.delete_competition", raise_exception=True)
def competition_delete(request: HttpRequest, selected_event_id: int, competition_id: int) -> HttpResponse:
    c = get_object_or_404(Competition, pk=competition_id)
    c.delete()
    logger.info(
        "Competition '%s' deleted.", c.name, extra={"user": request.user, "event_id": selected_event_id}
    )
    return HttpResponseRedirect(reverse("manage-kompomaatti:competitions", args=(selected_event_id,)))


@staff_access_required
def compo_browse(request: HttpRequest, selected_event_id: int) -> HttpResponse:
    compos = Compo.objects.filter(event_id=selected_event_id)

    # Handle copying of old compos
    if request.method == "POST" and "submit-clone" in request.POST:
        if not request.user.has_perm("kompomaatti.add_compo"):
            raise PermissionDenied()

        clone_compo_form = CloneCompoForm(request.POST)
        if clone_compo_form.is_valid():
            clone_compo_form.save(event_id=selected_event_id)
            logger.info(
                "Compos from other event cloned",
                extra={"user": request.user, "event_id": selected_event_id},
            )
            return HttpResponseRedirect(reverse("manage-kompomaatti:compos", args=(selected_event_id,)))
    else:
        clone_compo_form = CloneCompoForm()

    # Handle adding a new compo
    if request.method == "POST" and "submit-compo" in request.POST:
        if not request.user.has_perm("kompomaatti.add_compo"):
            raise PermissionDenied()

        compo_form = AdminCompoForm(request.POST)
        if compo_form.is_valid():
            data = compo_form.save(commit=False)
            data.event_id = selected_event_id
            data.save()
            logger.info(
                "Compo '%s' added.", data.name, extra={"user": request.user, "event_id": selected_event_id}
            )
            return HttpResponseRedirect(reverse("manage-kompomaatti:compos", args=(selected_event_id,)))
    else:
        compo_form = AdminCompoForm()

    return admin_render(
        request,
        "admin_kompomaatti/compo_browse.html",
        {
            "compos": compos,
            "compoform": compo_form,
            "clonecompoform": clone_compo_form,
            "selected_event_id": selected_event_id,
        },
    )


@staff_access_required
@permission_required("kompomaatti.change_compo", raise_exception=True)
def compo_edit(request: HttpRequest, selected_event_id: int, compo_id: int) -> HttpResponse:
    compo = get_object_or_404(Compo, pk=compo_id)

    if request.method == "POST":
        edit_form = AdminCompoForm(request.POST, instance=compo)
        if edit_form.is_valid():
            c = edit_form.save()
            logger.info(
                "Compo '%s' edited.", c.name, extra={"user": request.user, "event_id": selected_event_id}
            )
            return HttpResponseRedirect(reverse("manage-kompomaatti:compos", args=(selected_event_id,)))
    else:
        edit_form = AdminCompoForm(instance=compo)

    # Render response
    return admin_render(
        request,
        "admin_kompomaatti/compo_edit.html",
        {"compo": compo, "editform": edit_form, "selected_event_id": selected_event_id},
    )


@staff_access_required
@permission_required("kompomaatti.delete_compo", raise_exception=True)
def compo_delete(request: HttpRequest, selected_event_id: int, compo_id: int) -> HttpResponse:
    c = get_object_or_404(Compo, pk=compo_id)
    c.delete()
    logger.info("Compo '%s' deleted.", c.name, extra={"user": request.user, "event_id": selected_event_id})
    return HttpResponseRedirect(reverse("manage-kompomaatti:compos", args=(selected_event_id,)))


@staff_access_required
def entry_browse(request: HttpRequest, selected_event_id: int) -> HttpResponse:
    event = get_object_or_404(Event, pk=selected_event_id)

    if request.method == "POST":
        if not request.user.has_perm("kompomaatti.add_entry"):
            raise PermissionDenied()

        entry_form = AdminEntryAddForm(request.POST, request.FILES, event=event)
        if entry_form.is_valid():
            e = entry_form.save()
            logger.info(
                "Compo entry '%s' added.",
                e.name,
                extra={"user": request.user, "event_id": selected_event_id},
            )
            return HttpResponseRedirect(reverse("manage-kompomaatti:entries", args=(selected_event_id,)))
    else:
        entry_form = AdminEntryAddForm(event=event)

    compos = Compo.objects.filter(event=selected_event_id)
    entries = Entry.objects.filter(compo__in=compos)
    return admin_render(
        request,
        "admin_kompomaatti/entry_browse.html",
        {"entries": entries, "entryform": entry_form, "selected_event_id": selected_event_id},
    )


@staff_access_required
@permission_required("kompomaatti.change_entry", raise_exception=True)
def entry_edit(request: HttpRequest, selected_event_id: int, entry_id: int) -> HttpResponse:
    entry = get_object_or_404(Entry, pk=entry_id)
    event = get_object_or_404(Event, pk=selected_event_id)

    if request.method == "POST":
        edit_form = AdminEntryEditForm(request.POST, request.FILES, instance=entry, event=event)
        if edit_form.is_valid():
            e = edit_form.save()
            logger.info(
                "Compo entry '%s' edited.",
                e.name,
                extra={"user": request.user, "event_id": selected_event_id},
            )
            return HttpResponseRedirect(reverse("manage-kompomaatti:entries", args=(selected_event_id,)))
    else:
        edit_form = AdminEntryEditForm(instance=entry, event=event)

    return admin_render(
        request,
        "admin_kompomaatti/entry_edit.html",
        {"entry": entry, "editform": edit_form, "selected_event_id": selected_event_id},
    )


@staff_access_required
@permission_required("kompomaatti.delete_entry", raise_exception=True)
def entry_delete(request: HttpRequest, selected_event_id: int, entry_id: int) -> HttpResponse:
    entry = get_object_or_404(Entry, pk=entry_id)
    entry.delete()
    logger.info(
        "Compo entry '%s' deleted.", entry.name, extra={"user": request.user, "event_id": selected_event_id}
    )
    return HttpResponseRedirect(reverse("manage-kompomaatti:entries", args=(selected_event_id,)))


@staff_access_required
def results(request: HttpRequest, selected_event_id: int) -> HttpResponse:
    compos = Compo.objects.filter(event_id=selected_event_id)
    competitions = Competition.objects.filter(event_id=selected_event_id)

    # Get the entries
    compo_results = {}
    for compo in compos:
        compo_results[compo] = entrysort.sort_by_score(Entry.objects.filter(compo=compo))

    # Get competition participations
    competition_results = {}
    for competition in competitions:
        rank_by = "score" if competition.score_sort == 1 else "-score"
        competition_results[competition.name] = CompetitionParticipation.objects.filter(
            competition=competition
        ).order_by(rank_by)

    return admin_render(
        request,
        "admin_kompomaatti/results.html",
        {
            "compo_results": compo_results,
            "competition_results": competition_results,
            "selected_event_id": selected_event_id,
        },
    )


@staff_access_required
def ticket_vote_codes(request: HttpRequest, selected_event_id: int) -> HttpResponse:
    tokens = TicketVoteCode.objects.filter(event_id=selected_event_id)
    return admin_render(
        request,
        "admin_kompomaatti/ticketvotecodes.html",
        {"tokens": tokens, "selected_event_id": selected_event_id},
    )


@staff_access_required
def vote_code_requests(request: HttpRequest, selected_event_id: int) -> HttpResponse:
    requests = VoteCodeRequest.objects.filter(event_id=selected_event_id)
    return admin_render(
        request,
        "admin_kompomaatti/vcrequests.html",
        {"requests": requests, "selected_event_id": selected_event_id},
    )


@staff_access_required
@permission_required("kompomaatti.change_votecode", raise_exception=True)
def accept_vote_code_request(
    request: HttpRequest, selected_event_id: int, vote_code_request_id: int
) -> HttpResponse:
    vcr = get_object_or_404(VoteCodeRequest, pk=vote_code_request_id)
    logger.info(
        "Votecode request from '%s' accepted.",
        vcr.user.username,
        extra={"user": request.user, "event_id": selected_event_id},
    )
    vcr.status = 1
    vcr.save()

    return HttpResponseRedirect(reverse("manage-kompomaatti:votecoderequests", args=(selected_event_id,)))


@staff_access_required
@permission_required("kompomaatti.change_votecode", raise_exception=True)
def reject_vote_code_request(
    request: HttpRequest, selected_event_id: int, vote_code_request_id: int
) -> HttpResponse:
    vcr = get_object_or_404(VoteCodeRequest, pk=vote_code_request_id)
    logger.info(
        "Votecode request from '%s' rejected.",
        vcr.user.username,
        extra={"user": request.user, "event_id": selected_event_id},
    )
    vcr.status = 2
    vcr.save()

    return HttpResponseRedirect(reverse("manage-kompomaatti:votecoderequests", args=(selected_event_id,)))
