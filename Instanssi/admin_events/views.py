import logging

from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse

from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.admin_events.forms import EventForm
from Instanssi.common.auth import staff_access_required
from Instanssi.kompomaatti.models import Event

logger = logging.getLogger(__name__)


@staff_access_required
def index(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        if not request.user.has_perm("kompomaatti.add_event"):
            raise PermissionDenied()

        event_form = EventForm(request.POST)
        if event_form.is_valid():
            data = event_form.save(commit=False)
            data.archived = False
            data.save()
            logger.info("Event %s added", data.name, extra={"user": request.user})
            return HttpResponseRedirect(reverse("manage-events:index"))
    else:
        event_form = EventForm()

    events = Event.objects.all()
    return admin_render(request, "admin_events/index.html", {"events": events, "eventform": event_form})


@staff_access_required
@permission_required("kompomaatti.change_event", raise_exception=True)
def edit(request: HttpRequest, event_id: int) -> HttpResponse:
    event = get_object_or_404(Event, pk=event_id)
    if request.method == "POST":
        event_form = EventForm(request.POST, instance=event)
        if event_form.is_valid():
            data = event_form.save(commit=False)
            data.archived = False
            data.save()
            logger.info("Event %s edited", data.name, extra={"user": request.user})
            return HttpResponseRedirect(reverse("manage-events:index"))
    else:
        event_form = EventForm(instance=event)

    return admin_render(request, "admin_events/edit.html", {"eventform": event_form})


@staff_access_required
@permission_required("kompomaatti.delete_event", raise_exception=True)
def delete(request: HttpRequest, event_id: int) -> HttpResponse:
    event = get_object_or_404(Event, pk=event_id)
    event.delete()
    logger.info("Event %s deleted", event.name, extra={"user": request.user})
    return HttpResponseRedirect(reverse("manage-events:index"))
