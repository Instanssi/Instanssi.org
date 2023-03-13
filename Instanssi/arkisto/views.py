from copy import copy

from django.http import Http404, HttpRequest, HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, render

from Instanssi.arkisto.models import OtherVideo, OtherVideoCategory
from Instanssi.kompomaatti.misc import entrysort
from Instanssi.kompomaatti.models import (
    Competition,
    CompetitionParticipation,
    Compo,
    Entry,
    Event,
)


def text_event(request: HttpRequest, event_id: int) -> HttpResponse:
    event = get_object_or_404(Event, pk=event_id, archived=True)

    # Get all compos that are active but not hidden from archive
    compos = []
    for compo in Compo.objects.filter(event=event, active=True, hide_from_archive=False):
        if compo.show_voting_results:
            compo.entries = entrysort.sort_by_score(Entry.objects.filter(compo=compo))
        else:
            compo.entries = Entry.objects.filter(compo=compo).order_by("name")
        compos.append(compo)

    return render(
        request,
        "arkisto/results.txt",
        {"event": event, "compos": compos},
        content_type="text/plain; charset=utf-8",
    )


def json_event(request: HttpRequest, event_id: int) -> HttpResponse:
    event = get_object_or_404(Event, pk=event_id, archived=True)

    # Get all compos that are active but not hidden from archive
    entries_out = []
    compos_out = []
    for c in Compo.objects.filter(event=event, active=True, hide_from_archive=False):
        if c.show_voting_results:
            entries = entrysort.sort_by_score(Entry.objects.filter(compo=c))
        else:
            entries = Entry.objects.filter(compo=c).order_by("name")

        compos_out.append({"id": c.pk, "name": c.name, "entry_count": len(entries)})

        for e in entries:
            entries_out.append(
                {
                    "id": e.id,
                    "compo_name": c.name,
                    "compo_id": c.pk,
                    "entry_name": e.name,
                    "entry_author": e.creator,
                    "entry_score": round(e.get_score(), 2),
                    "entry_rank": e.get_rank(),
                    "entry_result_url": request.build_absolute_uri(e.entryfile.url),
                    "entry_source_url": request.build_absolute_uri(e.sourcefile.url)
                    if e.sourcefile
                    else None,
                    "entry_youtube_url": e.youtube_url.link_url if e.youtube_url else None,
                    "entry_image_thumbnail": request.build_absolute_uri(e.imagefile_thumbnail.url)
                    if e.imagefile_thumbnail
                    else None,
                    "entry_image_medium": request.build_absolute_uri(e.imagefile_medium.url)
                    if e.imagefile_medium
                    else None,
                    "entry_image_original": request.build_absolute_uri(e.imagefile_original.url)
                    if e.imagefile_original
                    else None,
                }
            )

    return JsonResponse({"entries": entries_out, "compos": compos_out})


def event_index(request, event_id):
    event = get_object_or_404(Event, pk=event_id, archived=True)

    # Filter compos, videos and competitions
    compos_q = Compo.objects.filter(event=event, active=True, hide_from_archive=False).order_by("name")
    videos_q = OtherVideoCategory.objects.filter(event=event).order_by("name")
    competitions_q = Competition.objects.filter(event=event, active=True, hide_from_archive=False).order_by(
        "name"
    )

    # Get all compos that are active but not hidden from archive
    compo_list = []
    for compo in compos_q:
        if compo.show_voting_results:
            compo.entries = entrysort.sort_by_score(Entry.objects.filter(compo=compo))
        else:
            compo.entries = Entry.objects.filter(compo=compo).order_by("name")
        compo_list.append(copy(compo))

    # Get other videos
    video_list = []
    for cat in videos_q:
        cat.videos = OtherVideo.objects.filter(category=cat)
        video_list.append(copy(cat))

    # Get competitions
    competition_list = []
    for comp in competitions_q:
        rank_by = "score" if comp.score_sort == 1 else "-score"
        comp.participants = CompetitionParticipation.objects.filter(competition=comp).order_by(rank_by)
        competition_list.append(copy(comp))

    # Render Event frontpage
    return render(
        request,
        "arkisto/index.html",
        {"event": event, "compos": compo_list, "videos": video_list, "competitions": competition_list},
    )


# Index page (loads event page)
def index(request: HttpRequest) -> HttpResponse:
    try:
        latest = Event.objects.filter(archived=True).latest("date")
    except Event.DoesNotExist:
        return render(request, "arkisto/empty.html")

    return event_index(request, latest.id)


# Entry page
def entry_index(request: HttpRequest, entry_id: int) -> HttpResponse:
    entry = get_object_or_404(Entry, pk=entry_id)

    # Make sure the entry belongs to an archived event
    if not entry.compo.event.archived:
        raise Http404

    # Make sure the compo is active and can be shown
    if entry.compo.hide_from_archive or not entry.compo.active:
        raise Http404

    # Dump the page
    return render(request, "arkisto/entry.html", {"entry": entry, "event": entry.compo.event})


# Video page
def video_index(request: HttpRequest, video_id: int) -> HttpResponse:
    video = get_object_or_404(OtherVideo, pk=video_id)
    if not video.category.event.archived:
        raise Http404

    return render(request, "arkisto/video.html", {"video": video, "event": video.category.event})
