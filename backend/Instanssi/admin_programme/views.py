import logging

from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse

from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.admin_programme.forms import ProgrammeEventForm
from Instanssi.common.auth import staff_access_required
from Instanssi.ext_programme.models import ProgrammeEvent

logger = logging.getLogger(__name__)


@staff_access_required
def index(request: HttpRequest, selected_event_id: int) -> HttpResponse:
    if request.method == "POST":
        if not request.user.has_perm("ext_programme.add_programmeevent"):
            raise PermissionDenied()

        form = ProgrammeEventForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.save(commit=False)
            data.event_id = selected_event_id
            data.save()
            logger.info(
                "Programme event '%s' added.",
                data.title,
                extra={"user": request.user, "event_id": selected_event_id},
            )
            return HttpResponseRedirect(reverse("manage-programme:index", args=(selected_event_id,)))
    else:
        form = ProgrammeEventForm()

    programme_events = ProgrammeEvent.objects.filter(event_id=selected_event_id)
    return admin_render(
        request,
        "admin_programme/index.html",
        {"programme_events": programme_events, "selected_event_id": selected_event_id, "eventform": form},
    )


@staff_access_required
@permission_required("ext_programme.change_programmeevent", raise_exception=True)
def edit(request: HttpRequest, selected_event_id: int, event_id: int) -> HttpResponse:
    programme_event = get_object_or_404(ProgrammeEvent, pk=event_id)

    if request.method == "POST":
        form = ProgrammeEventForm(request.POST, request.FILES, instance=programme_event)
        if form.is_valid():
            data = form.save()
            logger.info(
                "Programme event '%s' edited.",
                data.title,
                extra={"user": request.user, "event_id": selected_event_id},
            )
            return HttpResponseRedirect(reverse("manage-programme:index", args=(selected_event_id,)))
    else:
        form = ProgrammeEventForm(instance=programme_event)

    return admin_render(
        request,
        "admin_programme/edit.html",
        {"eventform": form, "event": programme_event, "selected_event_id": selected_event_id},
    )


@staff_access_required
@permission_required("ext_programme.delete_programmeevent", raise_exception=True)
def delete(request: HttpRequest, selected_event_id: int, event_id: int) -> HttpResponse:
    p = get_object_or_404(ProgrammeEvent, pk=event_id)
    p.delete()
    logger.info(
        "Programme event '%s' deleted.", p.title, extra={"user": request.user, "event_id": selected_event_id}
    )
    return HttpResponseRedirect(reverse("manage-programme:index", args=(selected_event_id,)))
