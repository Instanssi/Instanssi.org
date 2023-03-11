import logging

from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone

from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.admin_upload.forms import UploadForm
from Instanssi.admin_upload.models import UploadedFile
from Instanssi.common.auth import staff_access_required

logger = logging.getLogger(__name__)


@staff_access_required
def index(request: HttpRequest, selected_event_id: int) -> HttpResponse:
    if request.method == "POST":
        if not request.user.has_perm("admin_upload.add_uploadedfile"):
            raise PermissionDenied()

        upload_form = UploadForm(request.POST, request.FILES)
        if upload_form.is_valid():
            data = upload_form.save(commit=False)
            data.user = request.user
            data.date = timezone.now()
            data.event_id = selected_event_id
            data.save()
            logger.info(
                "File '%s' uploaded.",
                data.file.name,
                extra={"user": request.user, "event_id": selected_event_id},
            )
            return HttpResponseRedirect(reverse("manage-uploads:index", args=(selected_event_id,)))
    else:
        upload_form = UploadForm()

    files = UploadedFile.objects.filter(event_id=selected_event_id)
    return admin_render(
        request,
        "admin_upload/index.html",
        {"files": files, "uploadform": upload_form, "selected_event_id": selected_event_id},
    )


@staff_access_required
@permission_required("admin_upload.delete_uploadedfile", raise_exception=True)
def delete_file(request: HttpRequest, selected_event_id: int, file_id: int) -> HttpResponse:
    rec = get_object_or_404(UploadedFile, pk=file_id)
    rec.delete()
    logger.info(
        "File '%s' deleted.",
        rec.file.name,
        extra={"user": request.user, "event_id": selected_event_id},
    )
    return HttpResponseRedirect(reverse("manage-uploads:index", args=(selected_event_id,)))


@staff_access_required
@permission_required("admin_upload.change_uploadedfile", raise_exception=True)
def edit_file(request: HttpRequest, selected_event_id: int, file_id: int) -> HttpResponse:
    uploaded_file = get_object_or_404(UploadedFile, pk=file_id)

    if request.method == "POST":
        upload_form = UploadForm(request.POST, request.FILES, instance=uploaded_file)
        if upload_form.is_valid():
            data = upload_form.save()
            logger.info(
                "File '%s' edited.",
                data.file.name,
                extra={"user": request.user, "event_id": selected_event_id},
            )
            return HttpResponseRedirect(reverse("manage-uploads:index", args=(selected_event_id,)))
    else:
        upload_form = UploadForm(instance=uploaded_file)

    return admin_render(
        request,
        "admin_upload/edit.html",
        {"uploadform": upload_form, "selected_event_id": selected_event_id},
    )
