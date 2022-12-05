import logging

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.core.exceptions import BadRequest, PermissionDenied
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse

from Instanssi.admin_arkisto.forms import VideoCategoryForm, VideoForm
from Instanssi.admin_arkisto.misc import utils
from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.arkisto.models import OtherVideo, OtherVideoCategory
from Instanssi.common.auth import staff_access_required
from Instanssi.kompomaatti.models import (
    CompetitionParticipation,
    Compo,
    Entry,
    Event,
    Vote,
    VoteGroup,
)

logger = logging.getLogger(__name__)


@staff_access_required
def index(request: HttpRequest, selected_event_id: int) -> HttpResponse:
    return admin_render(request, "admin_arkisto/index.html", {"selected_event_id": selected_event_id})


@staff_access_required
@permission_required("kompomaatti.delete_vote", raise_exception=True)
def remove_old_votes(request: HttpRequest, selected_event_id: int) -> HttpResponse:
    # Don't proceed if the event is still ongoing
    event = get_object_or_404(Event, pk=selected_event_id)
    if utils.is_event_ongoing(event):
        raise BadRequest

    # Find compos belonging to this event
    compo_ids = Compo.objects.filter(event_id=selected_event_id).values("pk")

    # Don't allow removing votes if votes haven't yet been consolidated to entry rows (prevent data loss)
    if utils.is_votes_unoptimized(compo_ids):
        raise BadRequest

    # Delete votes belonging to compos in this event
    for group in VoteGroup.objects.filter(compo__in=compo_ids):
        group.delete_votes()
        group.delete()

    logger.info("Event old votes removed", extra={"user": request.user, "event": event})
    return HttpResponseRedirect(reverse("manage-arkisto:archiver", args=(selected_event_id,)))


@staff_access_required
@permission_required("kompomaatti.change_entry", raise_exception=True)
def transfer_rights(request: HttpRequest, selected_event_id: int) -> HttpResponse:
    # Don't allow this function if the event is still ongoing
    event = get_object_or_404(Event, pk=selected_event_id)
    if utils.is_event_ongoing(event):
        raise BadRequest

    # Transfer all user rights on entries and competition participations belonging to this event
    archive_user = get_object_or_404(User, username="arkisto")
    Entry.objects.filter(compo__event=event).update(user=archive_user)
    CompetitionParticipation.objects.filter(competition__event=event).update(user=archive_user)

    logger.info("Event rights transferred", extra={"user": request.user, "event": event})
    return HttpResponseRedirect(reverse("manage-arkisto:archiver", args=(selected_event_id,)))


@staff_access_required
@permission_required("kompomaatti.change_entry", raise_exception=True)
def optimizes_scores(request: HttpRequest, selected_event_id: int) -> HttpResponse:
    # Don't allow this function if the event is still ongoing
    event = get_object_or_404(Event, pk=selected_event_id)
    if utils.is_event_ongoing(event):
        raise BadRequest

    # Set score and rank to database, instead of having to calculate it every time we need it
    entries = Entry.objects.filter(compo__event=event)
    for entry in entries:
        entry.archive_rank = entry.get_rank()
        entry.archive_score = entry.get_score()
        entry.save()

    logger.info("Event scores optimized", extra={"user": request.user, "event": event})
    return HttpResponseRedirect(reverse("manage-arkisto:archiver", args=(selected_event_id,)))


@staff_access_required
def archiver(request: HttpRequest, selected_event_id: int) -> HttpResponse:
    event = get_object_or_404(Event, pk=selected_event_id)
    archive_user = get_object_or_404(User, username="arkisto")
    compo_ids = Compo.objects.filter(event_id=int(selected_event_id)).values("pk")

    # Check if there are any compo/competition entries that are not owner by archive user
    has_non_archived_items = Entry.objects.filter(compo__in=compo_ids).exclude(user=archive_user).exists()
    if not has_non_archived_items:
        has_non_archived_items = (
            CompetitionParticipation.objects.filter(competition__event=event)
            .exclude(user=archive_user)
            .exists()
        )

    # Check if voting results need to be optimized
    votes_unoptimized = utils.is_votes_unoptimized(compo_ids)

    # Check if event is still ongoing
    ongoing_activity = utils.is_event_ongoing(event)

    # See if there are any old votes left
    old_votes_found = Vote.objects.filter(compo__in=compo_ids).exists()

    # Render response
    return admin_render(
        request,
        "admin_arkisto/archiver.html",
        {
            "selected_event_id": int(selected_event_id),
            "is_archived": event.archived,
            "has_non_archived_items": has_non_archived_items,
            "ongoing_activity": ongoing_activity,
            "votes_unoptimized": votes_unoptimized,
            "old_votes_found": old_votes_found,
        },
    )


@staff_access_required
@permission_required("kompomaatti.change_event", raise_exception=True)
def show(request: HttpRequest, selected_event_id: int) -> HttpResponse:
    event = get_object_or_404(Event, pk=selected_event_id)
    event.archived = True
    event.save()
    logger.info("Event set as visible in archive", extra={"user": request.user, "event": event})
    return HttpResponseRedirect(reverse("manage-arkisto:archiver", args=(selected_event_id,)))


@staff_access_required
@permission_required("kompomaatti.change_event", raise_exception=True)
def hide(request: HttpRequest, selected_event_id: int) -> HttpResponse:
    event = get_object_or_404(Event, pk=selected_event_id)
    event.archived = False
    event.save()
    logger.info("Event set as hidden in archive", extra={"user": request.user, "event": event})
    return HttpResponseRedirect(reverse("manage-arkisto:archiver", args=(selected_event_id,)))


@staff_access_required
@permission_required("arkisto.add_othervideo", raise_exception=True)
def videos(request: HttpRequest, selected_event_id: int) -> HttpResponse:
    event = get_object_or_404(Event, pk=selected_event_id)

    if request.method == "POST":
        video_form = VideoForm(request.POST, event=event)
        if video_form.is_valid():
            video = video_form.save()
            logger.info(
                "Added archive video %s",
                video.name,
                extra={"user": request.user, "event": event},
            )
            return HttpResponseRedirect(reverse("manage-arkisto:vids", args=(selected_event_id,)))
    else:
        video_form = VideoForm(event=event)

    event_videos = OtherVideo.objects.filter(category__event=event)

    return admin_render(
        request,
        "admin_arkisto/vids.html",
        {"videos": event_videos, "vidform": video_form, "selected_event_id": selected_event_id},
    )


@staff_access_required
@permission_required("arkisto.change_othervideo", raise_exception=True)
def edit_video(request: HttpRequest, selected_event_id: int, video_id: int) -> HttpResponse:
    video = get_object_or_404(OtherVideo, pk=video_id)
    event = get_object_or_404(Event, pk=selected_event_id)

    if request.method == "POST":
        video_form = VideoForm(request.POST, instance=video, event=event)
        if video_form.is_valid():
            r_video = video_form.save()
            logger.info(
                "Edited archive video %s",
                r_video.name,
                extra={"user": request.user, "event": event},
            )
            return HttpResponseRedirect(reverse("manage-arkisto:vids", args=(selected_event_id,)))
    else:
        video_form = VideoForm(instance=video, event=event)

    # Render response
    return admin_render(
        request,
        "admin_arkisto/editvid.html",
        {"vidform": video_form, "vid": video, "selected_event_id": selected_event_id},
    )


@staff_access_required
@permission_required("arkisto.delete_othervideo", raise_exception=True)
def delete_video(request: HttpRequest, selected_event_id: int, video_id: int) -> HttpResponse:
    event = get_object_or_404(Event, pk=selected_event_id)
    try:
        video = OtherVideo.objects.get(id=video_id)
        video.delete()
        logger.info("Deleted archive video %s", video.name, extra={"user": request.user, "event": event})
    except OtherVideo.DoesNotExist:
        pass

    # Redirect
    return HttpResponseRedirect(reverse("manage-arkisto:vids", args=(selected_event_id,)))


@staff_access_required
def video_categories(request: HttpRequest, selected_event_id: int) -> HttpResponse:
    event = get_object_or_404(Event, pk=selected_event_id)
    if request.method == "POST":
        if not request.user.has_perm("arkisto.add_othervideocategory"):
            raise PermissionDenied

        # Handle form
        cat_form = VideoCategoryForm(request.POST)
        if cat_form.is_valid():
            cat = cat_form.save(commit=False)
            cat.event = event
            cat.save()
            logger.info(
                "Added archive video category %s", cat.name, extra={"user": request.user, "event": event}
            )
            return HttpResponseRedirect(reverse("manage-arkisto:vidcats", args=(selected_event_id,)))
    else:
        cat_form = VideoCategoryForm()

    # Get videos belonging to selected event
    categories = OtherVideoCategory.objects.filter(event_id=int(selected_event_id))

    return admin_render(
        request,
        "admin_arkisto/cats.html",
        {"categories": categories, "catform": cat_form, "selected_event_id": int(selected_event_id)},
    )


@staff_access_required
@permission_required("arkisto.change_othervideocategory", raise_exception=True)
def edit_video_category(request: HttpRequest, selected_event_id: int, category_id: int) -> HttpResponse:
    event = get_object_or_404(Event, pk=selected_event_id)
    category = get_object_or_404(OtherVideoCategory, pk=category_id, event=event)

    if request.method == "POST":
        cat_form = VideoCategoryForm(request.POST, instance=category)
        if cat_form.is_valid():
            r_cat = cat_form.save()
            logger.info(
                "Edited archive video category %s",
                r_cat.name,
                extra={"user": request.user, "event": event},
            )
            return HttpResponseRedirect(reverse("manage-arkisto:vidcats", args=(selected_event_id,)))
    else:
        cat_form = VideoCategoryForm(instance=category)

    return admin_render(
        request,
        "admin_arkisto/editcat.html",
        {"catform": cat_form, "cat": category, "selected_event_id": int(selected_event_id)},
    )


@staff_access_required
@permission_required("arkisto.delete_othervideocategory", raise_exception=True)
def delete_video_category(request: HttpRequest, selected_event_id: int, category_id: int) -> HttpResponse:
    event = get_object_or_404(Event, pk=selected_event_id)

    try:
        cat = OtherVideoCategory.objects.get(id=category_id, event=event)
        cat.delete()
        logger.info(
            "Deleted archive video category %s",
            cat.name,
            extra={"user": request.user, "event": event},
        )
    except OtherVideoCategory.DoesNotExist:
        raise Http404

    return HttpResponseRedirect(reverse("manage-arkisto:vidcats", args=(selected_event_id,)))
