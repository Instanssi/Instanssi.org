import os
from pathlib import Path
from typing import Any

from django.core.files.uploadedfile import UploadedFile
from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError

from Instanssi.kompomaatti.models import Compo, Entry


def validate_entry_files(data: dict[str, Any], compo: Compo, instance: Entry | None = None) -> None:
    """Validate entry files against compo settings.

    Checks file format (extension), file size, and image file requirements.
    Raises ValidationError if any validation fails.
    """
    # Check if image file is required but missing
    image_file = data.get("imagefile_original")
    if not image_file and not (instance and instance.imagefile_original):
        if compo.is_imagefile_required:
            raise ValidationError({"imagefile_original": [_("Image file is required for this compo")]})

    # Check if image file is provided but not allowed
    if image_file and not compo.is_imagefile_allowed:
        raise ValidationError({"imagefile_original": [_("Image file is not allowed for this compo")]})

    # File validation configuration per field
    check_files_on = {
        "entryfile": (
            compo.entry_format_list,
            compo.readable_entry_formats,
            compo.max_entry_size,
            compo.readable_max_entry_size,
        ),
        "sourcefile": (
            compo.source_format_list,
            compo.readable_source_formats,
            compo.max_source_size,
            compo.readable_max_source_size,
        ),
        "imagefile_original": (
            compo.image_format_list,
            compo.readable_image_formats,
            compo.max_image_size,
            compo.readable_max_image_size,
        ),
    }

    # Validate each file and aggregate errors
    errors = {}
    for key, args in check_files_on.items():
        if file := data.get(key):
            field_errors = _validate_file(file, *args)
            if field_errors:
                errors[key] = field_errors

    if errors:
        raise ValidationError(errors)


def maybe_copy_entry_to_image(instance: Entry) -> None:
    """If necessary, copy entry file to image file for thumbnail generation."""
    if instance.compo.is_imagefile_copied and instance.entryfile:
        name = os.path.basename(instance.entryfile.name)
        instance.imagefile_original.save(name, instance.entryfile)


def _validate_file(
    file: UploadedFile,
    accept_formats: list[str],
    accept_formats_readable: str,
    max_size: int,
    max_readable_size: str,
) -> list[str]:
    """Validate file size and format, returning list of error messages."""
    errors: list[str] = []

    # Check file size
    if file.size is not None and file.size > max_size:
        errors.append(_("Maximum allowed file size is %(size)s") % {"size": max_readable_size})

    # Check file extension — use all suffixes so that e.g. ".tar.gz" is
    # matched as "tar.gz" first, falling back to the last suffix alone ("gz").
    if file.name:
        all_ext = "".join(Path(file.name).suffixes).lower().lstrip(".")
        last_ext = Path(file.name).suffix.lower().lstrip(".")
        if all_ext not in accept_formats and last_ext not in accept_formats:
            errors.append(_("Allowed file types are %(types)s") % {"types": accept_formats_readable})

    return errors
