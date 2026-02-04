import logging
from pathlib import Path
from typing import Final

import ffmpeg
from celery import shared_task
from django.core.files import File
from django.utils import timezone

from ..common.file_handling import temp_file
from .enums import MediaCodec, MediaContainer
from .models import AlternateEntryFile, Entry

log = logging.getLogger(__name__)


# Predefined bit-rates for known formats. Otherwise, use a guess.
FFMPEG_BITRATE: Final[dict[MediaCodec, str]] = {
    MediaCodec.OPUS: "64k",
    MediaCodec.AAC: "128k",
}

# Map codec to ffmpeg encoder name
FFMPEG_ENCODERS: Final[dict[MediaCodec, str]] = {
    MediaCodec.AAC: "aac",
    MediaCodec.OPUS: "libopus",
}


@shared_task(autoretry_for=[Entry.DoesNotExist], retry_backoff=3, retry_kwargs={"max_retries": 3})  # type: ignore[untyped-decorator]
def generate_alternate_audio_files(entry_id: int, codec_index: int, container_index: int) -> None:
    output_codec = MediaCodec(codec_index)
    output_codec_name = output_codec.name.lower()
    output_container = MediaContainer(container_index)
    output_container_name = output_container.name.lower()
    entry = Entry.objects.get(pk=entry_id)
    source_file = Path(entry.entryfile.path)

    # Some quick sanity checks for the input.
    if not entry.is_audio:
        log.error("Unable to convert -- Input file is not an audio file")
        return

    log.info(
        "Received file %s for processing -- converting to %s/%s",
        source_file,
        output_codec_name,
        output_container_name,
    )

    # Create a temporary directory, and write the recoded audio file there.
    with temp_file(output_container_name) as output_file:
        log.info("Using temp file %s", output_file)
        try:
            input_file = ffmpeg.input(source_file.resolve())
            pipeline = ffmpeg.output(
                input_file.audio,
                filename=output_file,
                format=output_container_name,
                acodec=FFMPEG_ENCODERS[output_codec],
                audio_bitrate=FFMPEG_BITRATE[output_codec],
            )
            pipeline.global_args("-hide_banner", "-nostats", "-loglevel", "warning").run()
        except Exception as e:
            log.exception("Unable to convert -- %s", str(e))
            raise

        # Remove existing file and object, if any.
        params = dict(entry=entry, codec=output_codec, container=output_container)
        try:
            alt = AlternateEntryFile.objects.get(**params)
            alt.updated_at = timezone.now()
            alt.file.delete(save=False)
            log.info("Updating existing database entry")
        except AlternateEntryFile.DoesNotExist:
            alt = AlternateEntryFile(**params)
            log.info("Creating a new database entry")

        # Read in the temporary file, save to django storage and database.
        with open(output_file, "rb") as fd:
            alt.file.save(output_file, File(fd))
        alt.save()
        log.info("Entry processed; result saved to %s", alt.file.path)
