from datetime import datetime, time
from pathlib import Path

from auditlog.registry import auditlog
from django.conf import settings
from django.db import models
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from Instanssi.common.file_handling import clean_filename, generate_upload_path
from Instanssi.common.html.fields import SanitizedHtmlField
from Instanssi.kompomaatti.models import Event


def generate_icon_path(entry: "ProgrammeEvent", filename: str) -> str:
    slug = clean_filename(Path(filename).stem)
    dt = datetime.combine(entry.event.date, time(0, 0, 0, 0))
    return generate_upload_path(
        original_file=filename,
        path=settings.MEDIA_PROGRAMME_IMAGES,
        slug=slug,
        timestamp=dt,
    )


class ProgrammeEvent(models.Model):
    EVENT_TYPES = (
        (0, _("Simple")),
        (1, _("Detailed")),
    )

    event = models.ForeignKey(Event, verbose_name=_("Event"), on_delete=models.PROTECT)
    start = models.DateTimeField(_("Start"), db_index=True)
    end = models.DateTimeField(_("End"), null=True, blank=True)
    description = SanitizedHtmlField(_("Description"), blank=True)
    title = models.CharField(_("Title"), max_length=128)
    presenters = models.CharField(_("Presenters"), max_length=256, blank=True)
    presenters_titles = models.CharField(_("Titles"), max_length=256, blank=True)
    place = models.CharField(_("Place"), max_length=64, blank=True)

    # This is such a hackish solution that it makes me want to throw up. Oh well.
    icon_original = models.ImageField(
        _("Image 1"),
        max_length=255,
        upload_to=generate_icon_path,
        blank=True,
    )
    icon_small = ImageSpecField([ResizeToFill(64, 64)], source="icon_original", format="PNG")
    icon2_original = models.ImageField(
        _("Image 2"),
        max_length=255,
        upload_to=generate_icon_path,
        blank=True,
    )
    icon2_small = ImageSpecField([ResizeToFill(64, 64)], source="icon2_original", format="PNG")

    email = models.EmailField(_("Email"), blank=True)
    home_url = models.URLField(_("Home URL"), blank=True)
    twitter_url = models.URLField(_("Twitter"), blank=True)
    github_url = models.URLField(_("Github"), blank=True)
    facebook_url = models.URLField(_("Facebook"), blank=True)
    linkedin_url = models.URLField(_("LinkedIn"), blank=True)
    wiki_url = models.URLField(_("Wikipedia"), blank=True)
    event_type = models.IntegerField(
        _("Event type"),
        choices=EVENT_TYPES,
        default=0,
    )
    active = models.BooleanField(_("Active"), default=True)

    @property
    def short_start_time(self) -> str:
        if self.start:
            return date_format(self.start, "D H:i")
        return ""

    def __str__(self) -> str:
        return self.title


auditlog.register(ProgrammeEvent)
