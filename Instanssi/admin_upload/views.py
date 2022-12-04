import logging

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone

from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.admin_upload.forms import UploadForm
from Instanssi.admin_upload.models import UploadedFile
from Instanssi.common.auth import staff_access_required
from Instanssi.common.http import Http403

logger = logging.getLogger(__name__)


@staff_access_required
def index(request, sel_event_id):
    # Handle form data, if any
    if request.method == "POST":
        # Check for permissions
        if not request.user.has_perm("admin_upload.add_uploadedfile"):
            raise Http403

        # Handle form
        uploadform = UploadForm(request.POST, request.FILES)
        if uploadform.is_valid():
            data = uploadform.save(commit=False)
            data.user = request.user
            data.date = timezone.now()
            data.event_id = int(sel_event_id)
            data.save()
            logger.info(
                'File "{}" uploaded.'.format(data.file.name),
                extra={"user": request.user, "event_id": sel_event_id},
            )
            return HttpResponseRedirect(reverse("manage-uploads:index", args=(sel_event_id,)))
    else:
        uploadform = UploadForm()

    # Get filelist
    files = UploadedFile.objects.filter(event_id=sel_event_id)

    # Render response
    return admin_render(
        request,
        "admin_upload/index.html",
        {
            "files": files,
            "uploadform": uploadform,
            "selected_event_id": int(sel_event_id),
        },
    )


@staff_access_required
def deletefile(request, sel_event_id, file_id):
    # Check for permissions
    if not request.user.has_perm("admin_upload.delete_uploadedfile"):
        raise Http403

    # Delete the file
    try:
        rec = UploadedFile.objects.get(id=file_id)
        logger.info(
            'File "{}" deleted.'.format(rec.file.name),
            extra={"user": request.user, "event_id": sel_event_id},
        )
        rec.file.delete()
        rec.delete()
    except UploadedFile.DoesNotExist:
        pass

    return HttpResponseRedirect(reverse("manage-uploads:index", args=(sel_event_id,)))


@staff_access_required
def editfile(request, sel_event_id, file_id):
    # Check for permissions
    if not request.user.has_perm("admin_upload.change_uploadedfile"):
        raise Http403

    # Get previously uploaded file
    uploadedfile = get_object_or_404(UploadedFile, pk=file_id)

    # Handle form data
    if request.method == "POST":
        uploadform = UploadForm(request.POST, request.FILES, instance=uploadedfile)
        if uploadform.is_valid():
            data = uploadform.save()
            logger.info(
                'File "{}" edited.'.format(data.file.name),
                extra={"user": request.user, "event_id": sel_event_id},
            )
            return HttpResponseRedirect(reverse("manage-uploads:index", args=(sel_event_id,)))
    else:
        uploadform = UploadForm(instance=uploadedfile)

    # Render response
    return admin_render(
        request,
        "admin_upload/edit.html",
        {
            "uploadform": uploadform,
            "selected_event_id": int(sel_event_id),
        },
    )
