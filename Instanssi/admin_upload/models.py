import os.path
from typing import Any

from auditlog.registry import auditlog
from django.contrib.auth.models import User
from django.db import models

from Instanssi.kompomaatti.models import Event


class UploadedFile(models.Model):
    event = models.ForeignKey(Event, verbose_name="Tapahtuma", on_delete=models.PROTECT)
    user = models.ForeignKey(User, verbose_name="Käyttäjä", on_delete=models.CASCADE)
    description = models.TextField(
        "Kuvaus", help_text="Lyhyt kuvaus siitä, mihin/missä tiedostoa käytetään.", blank=True
    )
    file = models.FileField("Tiedosto", upload_to="files/")
    date = models.DateTimeField("Aika")

    def __str__(self) -> str:
        return "{} by {}".format(self.file.name, self.user.username)

    class Meta:
        verbose_name = "tiedosto"
        verbose_name_plural = "tiedostot"

    def name(self) -> str:
        return str(os.path.basename(self.file.name))

    def save(self, *args: Any, **kwargs: Any) -> None:
        # Delete old file when editing
        try:
            this = UploadedFile.objects.get(id=self.id)
            if this.file != self.file:
                this.file.delete(save=False)
        except UploadedFile.DoesNotExist:
            pass

        # Continue with normal save
        super(UploadedFile, self).save(*args, **kwargs)


auditlog.register(UploadedFile)
