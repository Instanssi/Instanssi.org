from __future__ import absolute_import, unicode_literals

import logging
import os
import tarfile
import tempfile
import uuid
from contextlib import contextmanager
from pathlib import Path

import ffmpeg
from celery import shared_task
from django.core.files import File

from .models import AlternateEntryFile, Compo, Entry, EntryCollection

log = logging.getLogger(__name__)

CONVERTABLE_INPUTS = [
    ".mp3",
    ".opus",
    ".aac",
    ".ogg",
    ".oga",
    ".flac",
    ".m4a",
]

BITRATE = {
    "opus": 128 * 1024,
    "aac": 256 * 1024,
}


@contextmanager
def temp_file(output_format: str):
    with tempfile.TemporaryDirectory() as tmp:
        with Path(tmp).with_name(f"{uuid.uuid4().hex[:6]}.{output_format}") as output_file:
            yield output_file


@shared_task(autoretry_for=[Entry.DoesNotExist], retry_backoff=5, retry_kwargs={"max_retries": 3})
def generate_alternate_files(entry_id: int, output_format: str) -> None:
    entry = Entry.objects.get(pk=entry_id)
    source_file = Path(entry.entryfile.path)
    if not source_file.is_file():
        log.info("Unable to convert -- Not a file")
        return
    if source_file.suffix not in CONVERTABLE_INPUTS:
        log.info("Unable to convert -- input format %s not supported", source_file.suffix)
        return

    # Create a temporary directory, and write the recoded audio file there.
    with temp_file(output_format) as output_file:
        try:
            input_file = ffmpeg.input(source_file.resolve())
            pipeline = ffmpeg.output(
                input_file.audio,
                filename=output_file,
                audio_bitrate=BITRATE[output_format],
            )
            pipeline.global_args("-hide_banner", "-nostats", "-loglevel", "warning").run()
        except Exception as e:
            log.exception("Unable to convert -- %s", str(e))
            raise

        # Remove existing file and object, if any.
        format_index = AlternateEntryFile.FORMAT_CHOICES.index(output_format)
        try:
            alt = AlternateEntryFile.objects.get(entry=entry, format=format_index)
            alt.file.delete()
        except AlternateEntryFile.DoesNotExist:
            alt = AlternateEntryFile(entry=entry, format=format_index)

        # Read in the temporary file, save to django storage and database.
        with open(output_file, "rb") as fd:
            file_name = f"{entry.name}_{entry.creator}.{output_format}"
            alt.file.save(file_name, File(fd))
        alt.save()


@shared_task
def rebuild_collection(compo_id: int):
    log.info("Running for compo id %s", compo_id)
    compo = Compo.objects.get(id=compo_id)
    entries = Entry.objects.filter(compo_id=compo_id)

    try:
        col = EntryCollection.objects.get(compo=compo)
        col.file.delete()
    except EntryCollection.DoesNotExist:
        col = EntryCollection(compo=compo)

    with tempfile.TemporaryFile() as fd:
        with tarfile.open(fileobj=fd, mode="w:gz") as tar:
            for entry in entries:
                _, ext = os.path.splitext(entry.entryfile.path)
                base_name = (
                    "{}-by-{}{}".format(entry.name, entry.creator, ext)
                    .replace(" ", "_")
                    .replace("/", "-")
                    .replace("\\", "-")
                    .replace("ä", "a")
                    .replace("ö", "o")
                    .encode("ascii", "ignore")
                    .decode("ascii")
                )
                log.info("Compressing to %s", base_name)
                with open(entry.entryfile.path, "rb") as in_fd:
                    tar_info = tarfile.TarInfo(base_name)
                    tar_info.size = entry.entryfile.size
                    tar.addfile(tarinfo=tar_info, fileobj=in_fd)
            tar.close()

        col_name = "{}_{}_{}.tar.gz".format(compo.event.name, compo.name, uuid.uuid4().hex[:6])
        col.file.save(name=col_name.encode("ascii", "ignore").decode("ascii"), content=File(fd))
        col.save()
        log.info("'%s' -> '%s'", col.compo, col.file)
