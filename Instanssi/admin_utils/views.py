# Logging related
import logging
import os

from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse

from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.common.auth import su_access_required
from Instanssi.kompomaatti.models import Entry

logger = logging.getLogger(__name__)

ENTRYDIR = os.path.join(settings.MEDIA_ROOT, "kompomaatti/entryfiles/")
SOURCEDIR = os.path.join(settings.MEDIA_ROOT, "kompomaatti/entrysources/")
IMAGEDIR = os.path.join(settings.MEDIA_ROOT, "kompomaatti/entryimages/")


@su_access_required
def diskcleaner(request):
    # Get entries
    entries = Entry.objects.all()
    db_efs = []
    db_sfs = []
    db_ifs = []
    for entry in entries:
        db_efs.append(os.path.basename(entry.entryfile.name))
        if entry.imagefile_original:
            db_ifs.append(os.path.basename(entry.imagefile_original.name))
        if entry.sourcefile:
            db_sfs.append(os.path.basename(entry.sourcefile.name))

    # Find orphaned entryfiles
    orphan_entryfiles = []
    for file in os.listdir(ENTRYDIR):
        if file not in db_efs:
            ext_path = os.path.join(settings.MEDIA_URL, "kompomaatti/entryfiles/") + file
            loc_path = os.path.join(ENTRYDIR, file)
            orphan_entryfiles.append(
                {
                    "path": ext_path,
                    "name": file,
                    "size": os.path.getsize(loc_path),
                    "local_path": loc_path,
                }
            )

    # Find orphaned entryfiles
    orphan_sourcefiles = []
    for file in os.listdir(SOURCEDIR):
        if file not in db_sfs:
            ext_path = os.path.join(settings.MEDIA_URL, "kompomaatti/entrysources/") + file
            loc_path = os.path.join(SOURCEDIR, file)
            orphan_sourcefiles.append(
                {
                    "path": ext_path,
                    "name": file,
                    "size": os.path.getsize(loc_path),
                    "local_path": loc_path,
                }
            )

    # Find orphaned entryfiles
    orphan_imagefiles = []
    for file in os.listdir(IMAGEDIR):
        if file not in db_ifs:
            ext_path = os.path.join(settings.MEDIA_URL, "kompomaatti/entryimages/") + file
            loc_path = os.path.join(IMAGEDIR, file)
            orphan_imagefiles.append(
                {
                    "path": ext_path,
                    "name": file,
                    "size": os.path.getsize(loc_path),
                    "local_path": loc_path,
                }
            )

    # Check if we need to do something
    if request.method == "POST" and "cleanup-button" in request.POST:
        for file in orphan_entryfiles:
            os.remove(file["local_path"])
        for file in orphan_sourcefiles:
            os.remove(file["local_path"])
        for file in orphan_imagefiles:
            os.remove(file["local_path"])
        logger.info("Diskcleaner run.", extra={"user": request.user})
        return HttpResponseRedirect(reverse("manage-utils:diskcleaner"))

    # Render response
    return admin_render(
        request,
        "admin_utils/diskcleaner.html",
        {
            "orphan_entryfiles": orphan_entryfiles,
            "orphan_sourcefiles": orphan_sourcefiles,
            "orphan_imagefiles": orphan_imagefiles,
        },
    )


@su_access_required
def dbchecker(request):
    entries = []
    for entry in Entry.objects.all():
        entry.entryfile_ok = True
        entry.sourcefile_ok = True
        entry.imagefile_ok = True
        if not os.path.exists(entry.entryfile.path):
            entry.entryfile_ok = False
        if entry.sourcefile and not os.path.exists(entry.sourcefile.path):
            entry.sourcefile_ok = False
        if entry.imagefile_original and not os.path.exists(entry.imagefile_original.path):
            entry.imagefile_ok = False

        if not entry.entryfile_ok or not entry.sourcefile_ok or not entry.imagefile_ok:
            entries.append(entry)

    # Render response
    return admin_render(
        request,
        "admin_utils/dbchecker.html",
        {
            "broken_entries": entries,
        },
    )


@su_access_required
def index(request):
    return admin_render(request, "admin_utils/index.html", {})
