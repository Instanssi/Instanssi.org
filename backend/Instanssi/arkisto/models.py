from auditlog.registry import auditlog
from django.db import models
from django.utils.translation import gettext_lazy as _

from Instanssi.common.youtube import YoutubeVideoField
from Instanssi.kompomaatti.models import Event


class OtherVideoCategory(models.Model):
    event = models.ForeignKey(Event, verbose_name=_("Event"), on_delete=models.PROTECT)
    name = models.CharField(_("Name"), max_length=64)

    def __str__(self) -> str:
        return self.name


class OtherVideo(models.Model):
    category = models.ForeignKey(OtherVideoCategory, verbose_name=_("Category"), on_delete=models.CASCADE)
    name = models.CharField(_("Name"), max_length=64)
    description = models.TextField(_("Description"))
    youtube_url = YoutubeVideoField(_("Youtube URL"))

    def __str__(self) -> str:
        return self.name


auditlog.register(OtherVideoCategory)
auditlog.register(OtherVideo)
