import tempfile
import uuid
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from secrets import token_urlsafe
from typing import Generator

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


def generate_upload_path(original_file: str, path: str, slug: str, timestamp: datetime) -> str:
    ext = Path(original_file).suffix.lstrip(".")
    path = path.rstrip("/")
    year = timestamp.year
    guid = token_urlsafe(4)
    return f"{path}/{year}/{slug}.{year}.{guid}.{ext}"
