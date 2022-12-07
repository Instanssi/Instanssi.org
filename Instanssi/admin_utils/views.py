import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Set
from urllib.parse import urljoin

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse

from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.common.auth import su_access_required
from Instanssi.kompomaatti.models import Entry

logger = logging.getLogger(__name__)

ENTRY_DIR = settings.MEDIA_ROOT / "kompomaatti" / "entryfiles"
SOURCE_DIR = settings.MEDIA_ROOT / "kompomaatti" / "entrysources"
IMAGE_DIR = settings.MEDIA_ROOT / "kompomaatti" / "entryimages"

ENTRY_MEDIA_URL = urljoin(settings.MEDIA_URL, "kompomaatti/entryfiles/")
SOURCE_MEDIA_URL = urljoin(settings.MEDIA_URL, "kompomaatti/entrysources/")
IMAGE_MEDIA_URL = urljoin(settings.MEDIA_URL, "kompomaatti/entryimages/")


@su_access_required
def diskcleaner(request: HttpRequest) -> HttpResponse:
    def find_orphans(search_dir: Path, root_url: str, whitelist: Set[str]) -> List[Dict[str, Any]]:
        orphans = []
        for iter_file in search_dir.iterdir():
            if not iter_file.is_file():
                continue
            if iter_file.name in whitelist:
                continue

            external_path = urljoin(root_url, iter_file.name)
            local_path = search_dir / iter_file.name
            file_size = os.path.getsize(local_path)
            orphans.append(
                {
                    "path": external_path,
                    "local_path": local_path,
                    "name": iter_file.name,
                    "size": file_size,
                }
            )
        return orphans

    entries = Entry.objects.all()
    db_entries = {os.path.basename(item.entryfile.name) for item in entries if item.entryfile}
    db_sources = {os.path.basename(item.sourcefile.name) for item in entries if item.sourcefile}
    db_images = {
        os.path.basename(item.imagefile_original.name) for item in entries if item.imagefile_original
    }

    orphan_entry_files = find_orphans(ENTRY_DIR, ENTRY_MEDIA_URL, db_entries)
    orphan_source_files = find_orphans(SOURCE_DIR, SOURCE_MEDIA_URL, db_sources)
    orphan_image_files = find_orphans(IMAGE_DIR, IMAGE_MEDIA_URL, db_images)

    # Check if we need to do something
    if request.method == "POST" and "cleanup-button" in request.POST:
        for file in orphan_entry_files:
            os.remove(file["local_path"])
        for file in orphan_source_files:
            os.remove(file["local_path"])
        for file in orphan_image_files:
            os.remove(file["local_path"])
        logger.info("Diskcleaner run", extra={"user": request.user})
        return HttpResponseRedirect(reverse("manage-utils:diskcleaner"))

    # Render response
    return admin_render(
        request,
        "admin_utils/diskcleaner.html",
        {
            "orphan_entryfiles": orphan_entry_files,
            "orphan_sourcefiles": orphan_source_files,
            "orphan_imagefiles": orphan_image_files,
        },
    )


@su_access_required
def db_checker(request: HttpRequest) -> HttpResponse:
    entries = []
    for entry in Entry.objects.all():
        entry.entryfile_ok = os.path.exists(entry.entryfile.path)
        entry.sourcefile_ok = not entry.sourcefile or os.path.exists(entry.sourcefile.path)
        entry.imagefile_ok = not entry.imagefile_original or os.path.exists(entry.imagefile_original.path)
        if not entry.entryfile_ok or not entry.sourcefile_ok or not entry.imagefile_ok:
            entries.append(entry)

    return admin_render(request, "admin_utils/dbchecker.html", {"broken_entries": entries})


@su_access_required
def index(request: HttpRequest) -> HttpResponse:
    return admin_render(request, "admin_utils/index.html", {})
