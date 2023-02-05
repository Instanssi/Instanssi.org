from auditlog.registry import auditlog
from django.db import models

from Instanssi.kompomaatti.models import Event


class OtherVideoCategory(models.Model):
    event = models.ForeignKey(Event, verbose_name="Tapahtuma", on_delete=models.PROTECT)
    name = models.CharField("Nimi", max_length=64, help_text="Kategorian nimi")

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "videokategoria"
        verbose_name_plural = "videokategoriat"


class OtherVideo(models.Model):
    category = models.ForeignKey(OtherVideoCategory, verbose_name="Kategoria", on_delete=models.CASCADE)
    name = models.CharField("Nimi", max_length=64, help_text="Videon nimi.")
    description = models.TextField("Kuvaus", help_text="Videon kuvaus.")
    youtube_url = models.URLField("Youtube URL", help_text="Linkki teoksen Youtube-versioon.", blank=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "muu video"
        verbose_name_plural = "muut videot"


auditlog.register(OtherVideoCategory)
auditlog.register(OtherVideo)
