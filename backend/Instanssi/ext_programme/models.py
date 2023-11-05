from datetime import datetime, time
from pathlib import Path
from typing import Any

import arrow
from auditlog.registry import auditlog
from django.conf import settings
from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from Instanssi.common.file_handling import clean_filename, generate_upload_path
from Instanssi.kompomaatti.models import Event

short_days = [
    "Ma",
    "Ti",
    "Ke",
    "To",
    "Pe",
    "La",
    "Su",
]


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
        (0, "Yksinkertainen"),
        (1, "Yksityiskohtainen"),
    )

    event = models.ForeignKey(Event, verbose_name="Tapahtuma", on_delete=models.PROTECT)
    start = models.DateTimeField("Alku", help_text="Tapahtuman alkamisaika.")
    end = models.DateTimeField("Loppu", help_text="Tapahtuman loppumisaika.", null=True, blank=True)
    description = models.TextField("Kuvaus", blank=True)
    title = models.CharField("Otsikko", help_text="Lyhyt otsikko.", max_length=128)
    presenters = models.CharField("Henkilöt", help_text="Esityksen pitäjät tms.", max_length=256, blank=True)
    presenters_titles = models.CharField(
        "Nimikkeet",
        help_text="Henkilön arvo-, ammatti- tai virkanimike.",
        max_length=256,
        blank=True,
    )
    place = models.CharField(
        "Paikka", help_text="Tarkka paikka tapahtuma-areenalla", max_length=64, blank=True
    )

    # This is such a hackish solution that it makes me want to throw up. Oh well.
    icon_original = models.ImageField(
        "Kuva 1", max_length=255, upload_to=generate_icon_path, help_text="Kuva 1 tapahtumalle.", blank=True
    )
    icon_small = ImageSpecField([ResizeToFill(64, 64)], source="icon_original", format="PNG")
    icon2_original = models.ImageField(
        "Kuva 2", max_length=255, upload_to=generate_icon_path, help_text="Kuva 2 tapahtumalle.", blank=True
    )
    icon2_small = ImageSpecField([ResizeToFill(64, 64)], source="icon2_original", format="PNG")

    email = models.EmailField(
        "Sähköposti",
        help_text="Tapahtumaan liittyvä sähköposti-osoite (esim. esiintyjän).",
        blank=True,
    )
    home_url = models.URLField("Kotiurli", help_text="Tapahtumaan liittyvä URL.", blank=True)
    twitter_url = models.URLField("Twitter", help_text="Tapahtumaan liittyvä Twitter-url.", blank=True)
    github_url = models.URLField("Github", help_text="Tapahtumaan liittyvä Github-url", blank=True)
    facebook_url = models.URLField("Facebook", help_text="Tapahtumaan liittyvä facebook-url.", blank=True)
    linkedin_url = models.URLField("LinkedIn", help_text="Tapahtumaan liittyvä LinkedIn-url.", blank=True)
    wiki_url = models.URLField("Wikipedia", help_text="Tapahtumaan liittyvä Wikipedia-url.", blank=True)
    event_type = models.IntegerField(
        "Tapahtuman tyyppi",
        choices=EVENT_TYPES,
        default=0,
        help_text="Määrittää tapahtuman tyypin. Yksityiskohtaiset tapahtumat näkyvät etusivun tapahtumalistassa.",
    )
    active = models.BooleanField("Aktiivinen", help_text="Deaktivoidut piilotetaan.", default=True)

    @property
    def short_start_time(self) -> str:
        if self.start:
            start = arrow.get(self.start).to(settings.TIME_ZONE)
            return "{} {}".format(short_days[start.weekday()], start.format("HH:mm"))
        return ""

    def save(self, *args: Any, **kwargs: Any) -> None:
        # Delete old icon file when editing
        try:
            this = ProgrammeEvent.objects.get(id=self.id)
            if this.icon_original != self.icon_original:
                this.icon_original.delete(save=False)
        except ProgrammeEvent.DoesNotExist:
            pass

        # Continue with normal save
        super(ProgrammeEvent, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "ohjelmatapahtuma"
        verbose_name_plural = "ohjelmatapahtumat"


auditlog.register(ProgrammeEvent)
