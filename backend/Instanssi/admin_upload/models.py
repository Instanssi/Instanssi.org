import os.path
from pathlib import Path

from auditlog.registry import auditlog
from django.conf import settings
from django.db import models
from django.utils import timezone

from Instanssi.common.file_handling import clean_filename, generate_upload_path
from Instanssi.kompomaatti.models import Event


def generate_file_path(entry: "UploadedFile", filename: str) -> str:
    slug = clean_filename(Path(filename).stem)
    return generate_upload_path(
        original_file=filename,
        path=settings.MEDIA_UPLOAD_FILES,
        slug=slug,
        timestamp=entry.date,
        group_by_year=False,
    )


class UploadedFile(models.Model):
    event = models.ForeignKey(Event, verbose_name="Tapahtuma", on_delete=models.PROTECT)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="Käyttäjä", on_delete=models.SET_NULL, null=True
    )
    description = models.TextField(
        "Kuvaus", help_text="Lyhyt kuvaus siitä, mihin/missä tiedostoa käytetään.", blank=True
    )
    file = models.FileField("Tiedosto", max_length=255, upload_to=generate_file_path)
    date = models.DateTimeField("Aika", default=timezone.now, db_index=True)

    def __str__(self) -> str:
        return str(self.file.name)

    class Meta:
        verbose_name = "tiedosto"
        verbose_name_plural = "tiedostot"

    def name(self) -> str:
        return str(os.path.basename(self.file.name))


auditlog.register(UploadedFile)
