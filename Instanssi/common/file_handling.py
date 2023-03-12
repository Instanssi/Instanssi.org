import tempfile
import uuid
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from secrets import token_urlsafe
from typing import Callable, Dict, Generator, List

from django.conf import settings
from django.db.models import QuerySet
from django.db.models.fields.files import FieldFile
from django.utils.text import slugify


def clean_filename(name: str) -> str:
    return slugify(name.replace(" ", "_").replace("ä", "a").replace("ö", "o").replace("å", "a"))


@contextmanager
def temp_file(output_format: str) -> Generator[Path, None, None]:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        tmp_file = f"tmp_{uuid.uuid4().hex}.{output_format}"
        with tmp_path.with_name(tmp_file) as output_file:
            yield output_file
            output_file.unlink()


def generate_upload_path(
    original_file: str, path: str, slug: str, timestamp: datetime, group_by_year: bool = True
) -> str:
    ext = Path(original_file).suffix.lstrip(".")
    path = path.rstrip("/")
    year = timestamp.year
    guid = token_urlsafe(4)
    filename = f"{slug}.{year}.{guid}.{ext}"
    if group_by_year:
        return f"{path}/{year}/{filename}"
    else:
        return f"{path}/{filename}"


class FileError(Exception):
    pass


def migrate_file_field(field: FieldFile, new_dir: str, dry_run: bool) -> None:
    src_path = (settings.MEDIA_ROOT / field.name).resolve()
    dst_path = (settings.MEDIA_ROOT / new_dir).resolve()
    if not src_path.exists():
        raise FileError(f"Source file does not exist: {src_path}")
    if dst_path.exists():
        raise FileError(f"Destination file already exists: {dst_path}")
    if dry_run:
        print(f"Faking move {src_path} to {dst_path}")
    else:
        print(f"Moving {src_path} to {dst_path}")
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        src_path.rename(dst_path)


def migrate_all_file_fields(qs: QuerySet, generators: Dict[str, Callable], dry_run: bool) -> List[str]:
    errors: List[str] = []
    for entry in qs:
        migrated: List[str] = []
        for field_name, generator in generators.items():
            try:
                field_file = getattr(entry, field_name)
                if field_file:
                    new_dir = generator(entry, field_file.name)
                    migrate_file_field(field_file, new_dir, dry_run)
                    field_file.name = new_dir
                    migrated.append(field_name)
            except FileError as err:
                errors.append(str(err))
        if not dry_run:
            entry.save(update_fields=migrated)
    return errors
