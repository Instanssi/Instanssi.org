import logging

from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse

from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.admin_screenshow.forms import (
    IRCMessageForm,
    MessageForm,
    PlaylistVideoForm,
    ScreenConfigForm,
    SponsorForm,
)
from Instanssi.common.auth import staff_access_required
from Instanssi.screenshow.models import (
    IRCMessage,
    Message,
    PlaylistVideo,
    ScreenConfig,
    Sponsor,
)

logger = logging.getLogger(__name__)


@staff_access_required
def index(request: HttpRequest, selected_event_id: int) -> HttpResponse:
    return admin_render(request, "admin_screenshow/index.html", {"selected_event_id": selected_event_id})


@staff_access_required
def config(request: HttpRequest, selected_event_id: int) -> HttpResponse:
    try:
        conf = ScreenConfig.objects.get(event_id=selected_event_id)
    except ScreenConfig.DoesNotExist:
        conf = None

    if request.method == "POST":
        if not request.user.has_perm("screenshow.change_screenconfig"):
            raise PermissionDenied()

        config_form = ScreenConfigForm(request.POST, instance=conf)
        if config_form.is_valid():
            data = config_form.save(commit=False)
            data.event_id = selected_event_id
            data.save()
            logger.info(
                "Screenshow configuration changed",
                extra={"user": request.user, "event_id": selected_event_id},
            )
            return HttpResponseRedirect(reverse("manage-screenshow:config", args=(selected_event_id,)))
    else:
        config_form = ScreenConfigForm(instance=conf)

    return admin_render(
        request,
        "admin_screenshow/config.html",
        {"selected_event_id": selected_event_id, "configform": config_form},
    )


@staff_access_required
def playlist(request: HttpRequest, selected_event_id: int) -> HttpResponse:
    if request.method == "POST":
        if not request.user.has_perm("screenshow.add_playlistvideo"):
            raise PermissionDenied()

        playlist_form = PlaylistVideoForm(request.POST)
        if playlist_form.is_valid():
            data = playlist_form.save(commit=False)
            data.event_id = selected_event_id
            data.save()
            logger.info(
                "Video '%s' added to playlist",
                data.name,
                extra={"user": request.user, "event_id": selected_event_id},
            )
            return HttpResponseRedirect(reverse("manage-screenshow:playlist", args=(selected_event_id,)))
    else:
        playlist_form = PlaylistVideoForm()

    videos = PlaylistVideo.objects.filter(event_id=selected_event_id).order_by("-index")
    return admin_render(
        request,
        "admin_screenshow/playlist.html",
        {"selected_event_id": selected_event_id, "videos": videos, "playlistform": playlist_form},
    )


@staff_access_required
@permission_required("screenshow.change_playlistvideo", raise_exception=True)
def playlist_edit(request: HttpRequest, selected_event_id: int, video_id: int) -> HttpResponse:
    playlist_video = get_object_or_404(PlaylistVideo, pk=video_id)

    if request.method == "POST":
        playlist_form = PlaylistVideoForm(request.POST, instance=playlist_video)
        if playlist_form.is_valid():
            v = playlist_form.save()
            logger.info(
                "Video '%s' edited on playlist",
                v.name,
                extra={"user": request.user, "event_id": selected_event_id},
            )
            return HttpResponseRedirect(reverse("manage-screenshow:playlist", args=(selected_event_id,)))
    else:
        playlist_form = PlaylistVideoForm(instance=playlist_video)

    return admin_render(
        request,
        "admin_screenshow/playlist_edit.html",
        {
            "selected_event_id": selected_event_id,
            "video_id": video_id,
            "playlistform": playlist_form,
        },
    )


@staff_access_required
@permission_required("screenshow.delete_playlistvideo", raise_exception=True)
def playlist_delete(request: HttpRequest, selected_event_id: int, video_id: int) -> HttpResponse:
    v = get_object_or_404(PlaylistVideo, pk=video_id)
    v.delete()
    logger.info(
        "Video '%s' deleted from playlist",
        v.name,
        extra={"user": request.user, "event_id": selected_event_id},
    )
    return HttpResponseRedirect(reverse("manage-screenshow:playlist", args=(selected_event_id,)))


@staff_access_required
def irc_messages(request: HttpRequest, selected_event_id: int) -> HttpResponse:
    return admin_render(
        request,
        "admin_screenshow/ircmessages.html",
        {
            "selected_event_id": selected_event_id,
            "messages": IRCMessage.objects.filter(event_id=selected_event_id),
        },
    )


@staff_access_required
@permission_required("screenshow.change_ircmessage", raise_exception=True)
def ircmessage_edit(request: HttpRequest, selected_event_id: int, message_id: int) -> HttpResponse:
    message = get_object_or_404(IRCMessage, pk=message_id)

    if request.method == "POST":
        message_form = IRCMessageForm(request.POST, instance=message)
        if message_form.is_valid():
            message_form.save()
            logger.info(
                "IRC Message '%s' edited",
                message.id,
                extra={"user": request.user, "event_id": selected_event_id},
            )
            return HttpResponseRedirect(reverse("manage-screenshow:ircmessages", args=(selected_event_id,)))
    else:
        message_form = IRCMessageForm(instance=message)

    return admin_render(
        request,
        "admin_screenshow/ircmessage_edit.html",
        {
            "selected_event_id": selected_event_id,
            "message_id": message_id,
            "messageform": message_form,
        },
    )


@staff_access_required
@permission_required("screenshow.delete_ircmessage", raise_exception=True)
def ircmessage_delete(request: HttpRequest, selected_event_id: int, message_id: int) -> HttpResponse:
    message = get_object_or_404(IRCMessage, pk=message_id)
    message.delete()
    logger.info(
        "IRC Message '%s' deleted",
        message.message[:10],
        extra={"user": request.user, "event_id": selected_event_id},
    )
    return HttpResponseRedirect(reverse("manage-screenshow:ircmessages", args=(selected_event_id,)))


@staff_access_required
def messages(request: HttpRequest, selected_event_id: int) -> HttpResponse:
    if request.method == "POST":
        if not request.user.has_perm("screenshow.add_message"):
            raise PermissionDenied()

        message_form = MessageForm(request.POST)
        if message_form.is_valid():
            data = message_form.save(commit=False)
            data.event_id = selected_event_id
            data.save()
            logger.info("Message added", extra={"user": request.user, "event_id": selected_event_id})
            return HttpResponseRedirect(reverse("manage-screenshow:messages", args=(selected_event_id,)))
    else:
        message_form = MessageForm()

    screen_messages = Message.objects.filter(event_id=selected_event_id)
    return admin_render(
        request,
        "admin_screenshow/messages.html",
        {"selected_event_id": selected_event_id, "messageform": message_form, "messages": screen_messages},
    )


@staff_access_required
@permission_required("screenshow.change_message", raise_exception=True)
def message_edit(request: HttpRequest, selected_event_id: int, message_id: int) -> HttpResponse:
    message = get_object_or_404(Message, pk=message_id)

    if request.method == "POST":
        message_form = MessageForm(request.POST, instance=message)
        if message_form.is_valid():
            message_form.save()
            logger.info("Message edited.", extra={"user": request.user, "event_id": selected_event_id})
            return HttpResponseRedirect(reverse("manage-screenshow:messages", args=(selected_event_id,)))
    else:
        message_form = MessageForm(instance=message)

    return admin_render(
        request,
        "admin_screenshow/message_edit.html",
        {"selected_event_id": selected_event_id, "message_id": message_id, "messageform": message_form},
    )


@staff_access_required
@permission_required("screenshow.delete_message", raise_exception=True)
def message_delete(request: HttpRequest, selected_event_id: int, message_id: int) -> HttpResponse:
    message = get_object_or_404(Message, pk=message_id)
    message.delete()
    logger.info("Message deleted.", extra={"user": request.user, "event_id": selected_event_id})
    return HttpResponseRedirect(reverse("manage-screenshow:messages", args=(selected_event_id,)))


@staff_access_required
def sponsors(request: HttpRequest, selected_event_id: int) -> HttpResponse:
    if request.method == "POST":
        if not request.user.has_perm("screenshow.add_sponsor"):
            raise PermissionDenied()

        sponsor_form = SponsorForm(request.POST, request.FILES)
        if sponsor_form.is_valid():
            data = sponsor_form.save(commit=False)
            data.event_id = selected_event_id
            data.save()
            logger.info(
                "Sponsor '%s' added",
                data.name,
                extra={"user": request.user, "event_id": selected_event_id},
            )
            return HttpResponseRedirect(reverse("manage-screenshow:sponsors", args=(selected_event_id,)))
    else:
        sponsor_form = SponsorForm()

    screen_sponsors = Sponsor.objects.filter(event_id=selected_event_id)
    return admin_render(
        request,
        "admin_screenshow/sponsors.html",
        {"selected_event_id": selected_event_id, "sponsorform": sponsor_form, "sponsors": screen_sponsors},
    )


@staff_access_required
@permission_required("screenshow.change_sponsor", raise_exception=True)
def sponsor_edit(request: HttpRequest, selected_event_id: int, sponsor_id: int) -> HttpResponse:
    sponsor = get_object_or_404(Sponsor, pk=sponsor_id)

    if request.method == "POST":
        sponsor_form = SponsorForm(request.POST, request.FILES, instance=sponsor)
        if sponsor_form.is_valid():
            s = sponsor_form.save()
            logger.info(
                "Sponsor '%s' edited",
                s.name,
                extra={"user": request.user, "event_id": selected_event_id},
            )
            return HttpResponseRedirect(reverse("manage-screenshow:sponsors", args=(selected_event_id,)))
    else:
        sponsor_form = SponsorForm(instance=sponsor)

    return admin_render(
        request,
        "admin_screenshow/sponsor_edit.html",
        {"selected_event_id": selected_event_id, "sponsor_id": sponsor_id, "sponsorform": sponsor_form},
    )


@staff_access_required
@permission_required("screenshow.delete_sponsor", raise_exception=True)
def sponsor_delete(request: HttpRequest, selected_event_id: int, sponsor_id: int) -> HttpResponse:
    sponsor = get_object_or_404(Sponsor, pk=sponsor_id)
    if sponsor.logo:
        sponsor.logo.delete()
    sponsor.delete()
    logger.info(
        "Sponsor '%s' deleted",
        sponsor.name,
        extra={"user": request.user, "event_id": selected_event_id},
    )
    return HttpResponseRedirect(reverse("manage-screenshow:sponsors", args=(selected_event_id,)))
