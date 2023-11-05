import logging

from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone

from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.admin_blog.forms import BlogEntryEditForm, BlogEntryForm
from Instanssi.common.auth import staff_access_required
from Instanssi.ext_blog.models import BlogEntry

logger = logging.getLogger(__name__)


@staff_access_required
def index(request: HttpRequest, selected_event_id: int) -> HttpResponse:
    if request.method == "POST":
        if not request.user.has_perm("ext_blog.add_blogentry"):
            raise PermissionDenied()

        form = BlogEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.event_id = selected_event_id
            entry.date = timezone.now()
            entry.user = request.user
            entry.save()
            logger.info(
                "Blog entry '%s' added.",
                entry.title,
                extra={"user": request.user, "event_id": selected_event_id},
            )
            return HttpResponseRedirect(reverse("manage-blog:index", args=(selected_event_id,)))
    else:
        form = BlogEntryForm()

    entries = BlogEntry.objects.filter(event_id=selected_event_id).order_by("date")
    return admin_render(
        request,
        "admin_blog/index.html",
        {"entries": entries, "selected_event_id": selected_event_id, "addform": form},
    )


@staff_access_required
@permission_required("ext_blog.change_blogentry", raise_exception=True)
def edit(request: HttpRequest, selected_event_id: int, entry_id: int) -> HttpResponse:
    entry = get_object_or_404(BlogEntry, pk=entry_id)

    if request.method == "POST":
        form = BlogEntryEditForm(request.POST, instance=entry)
        if form.is_valid():
            entry = form.save()
            logger.info(
                "Blog entry '%s' edited.",
                entry.title,
                extra={"user": request.user, "event_id": selected_event_id},
            )
            return HttpResponseRedirect(reverse("manage-blog:index", args=(selected_event_id,)))
    else:
        form = BlogEntryEditForm(instance=entry)

    return admin_render(
        request, "admin_blog/edit.html", {"editform": form, "selected_event_id": selected_event_id}
    )


@staff_access_required
@permission_required("ext_blog.delete_blogentry", raise_exception=True)
def delete(request: HttpRequest, selected_event_id: int, entry_id: int) -> HttpResponse:
    entry = get_object_or_404(BlogEntry, pk=entry_id)
    entry.delete()
    logger.info(
        "Blog entry '%s' deleted.", entry.title, extra={"user": request.user, "event_id": selected_event_id}
    )
    return HttpResponseRedirect(reverse("manage-blog:index", args=(selected_event_id,)))
