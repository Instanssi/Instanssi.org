from pathlib import Path
from typing import Any, Iterable

from auditlog.registry import auditlog
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from Instanssi.common.file_handling import clean_filename, generate_upload_path
from Instanssi.common.html.fields import SanitizedHtmlField
from Instanssi.common.youtube.fields import YoutubeVideoField
from Instanssi.kompomaatti.enums import (
    AUDIO_FILE_EXTENSIONS,
    WEB_AUDIO_FORMATS,
    MediaCodec,
    MediaContainer,
)
from Instanssi.kompomaatti.misc import sizeformat
from Instanssi.kompomaatti.querysets import (
    CompetitionParticipationQuerySet,
    EntryQuerySet,
)


class Event(models.Model):
    name = models.CharField(_("Name"), max_length=64, unique=True)
    tag = models.CharField(_("Short tag"), max_length=8, null=True, unique=True)
    date = models.DateField(_("Date"))
    archived = models.BooleanField(_("Archived"), default=False)
    hidden = models.BooleanField(_("Hidden"), default=False)
    mainurl = models.URLField(_("Event main page"), blank=True)

    def __str__(self) -> str:
        return self.name


class VoteCodeRequest(models.Model):
    STATUS_TYPES = (
        (0, _("Pending approval")),
        (1, _("Approved")),
        (2, _("Rejected")),
    )

    event = models.ForeignKey(
        Event,
        verbose_name=_("Event"),
        null=True,
        on_delete=models.PROTECT,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
    )
    text = models.TextField(_("Description"))
    status = models.IntegerField(_("Status"), choices=STATUS_TYPES, default=0)

    def __str__(self) -> str:
        return self.user.username

    class Meta:
        unique_together = (("event", "user"),)


class TicketVoteCode(models.Model):
    event = models.ForeignKey(
        Event,
        verbose_name=_("Event"),
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )
    associated_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    ticket = models.ForeignKey(
        "store.TransactionItem",  # String to avoid circular dependency
        verbose_name=_("Ticket item"),
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    time = models.DateTimeField(_("Timestamp"), blank=True, null=True)

    @property
    def key(self) -> str | None:
        if self.ticket:
            return self.ticket.key
        return None

    @property
    def associated_username(self) -> str | None:
        if self.associated_to:
            return self.associated_to.username
        return None

    def __str__(self) -> str:
        return "{}: {}".format(self.key, self.associated_username)

    class Meta:
        unique_together = (("event", "ticket"), ("event", "associated_to"))


class Compo(models.Model):
    MAX_IMAGE_SIZE = 6 * 1024 * 1024

    ENTRY_VIEW_TYPES = (
        (0, _("Nothing")),
        (1, _("Youtube first, then image")),
        (2, _("Image only")),
        (3, "(deprecated)"),
    )
    THUMBNAIL_REQ = (
        (0, _("Require separate thumbnail.")),
        (1, _("Use entry file as thumbnail (only works for png/jpg files).")),
        (2, _("Allow thumbnail (not required).")),
        (3, _("Do not allow thumbnail.")),
    )

    event = models.ForeignKey(
        Event,
        verbose_name=_("event"),
        on_delete=models.PROTECT,
    )
    name = models.CharField(_("Name"), max_length=32)
    description = SanitizedHtmlField(_("Description"))
    adding_end = models.DateTimeField(_("Entry adding deadline"))
    editing_end = models.DateTimeField(_("Entry editing deadline"))
    compo_start = models.DateTimeField(_("Compo start time"))
    voting_start = models.DateTimeField(_("Voting start time"))
    voting_end = models.DateTimeField(_("Voting end time"))
    entry_sizelimit = models.IntegerField(_("Entry size limit"), default=134217728)  # Default to 128M
    source_sizelimit = models.IntegerField(_("Source size limit"), default=134217728)  # Default to 128M
    formats = models.CharField(
        _("Allowed file extensions"),
        max_length=128,
        default="zip|7z|gz|bz2",
    )
    source_formats = models.CharField(
        _("Allowed source package extensions"),
        max_length=128,
        default="zip|7z|gz|bz2",
    )
    image_formats = models.CharField(
        _("Allowed image file extensions"),
        max_length=128,
        default="png|jpg",
    )
    active = models.BooleanField(_("Active"), default=True)
    show_voting_results = models.BooleanField(_("Show results"), default=False)
    entry_view_type = models.IntegerField(
        _("Entry presentation"),
        choices=ENTRY_VIEW_TYPES,
        default=0,
    )
    hide_from_archive = models.BooleanField(_("Hide from archive"), default=False)
    hide_from_frontpage = models.BooleanField(_("Hide from front page"), default=False)
    is_votable = models.BooleanField(_("Votable"), default=True)
    thumbnail_pref = models.IntegerField(
        _("Thumbnail settings"),
        choices=THUMBNAIL_REQ,
        default=2,
    )

    def __str__(self) -> str:
        return f"{self.event.name}: {self.name}"

    def is_voting_open(self) -> bool:
        if not self.is_votable:
            return False
        if self.voting_start <= timezone.now() < self.voting_end:
            return True
        return False

    def is_adding_open(self) -> bool:
        if timezone.now() < self.adding_end:
            return True
        return False

    def is_editing_open(self) -> bool:
        if timezone.now() < self.editing_end:
            return True
        return False

    def has_voting_started(self) -> bool:
        if not self.is_votable:
            return False
        if timezone.now() > self.voting_start:
            return True
        return False

    @property
    def entry_format_list(self) -> list[str]:
        return self.formats.lower().split("|")

    @property
    def source_format_list(self) -> list[str]:
        return self.source_formats.lower().split("|")

    @property
    def image_format_list(self) -> list[str]:
        return self.image_formats.lower().split("|")

    @property
    def readable_entry_formats(self) -> str:
        return ", ".join(self.entry_format_list)

    @property
    def readable_source_formats(self) -> str:
        return ", ".join(self.source_format_list)

    @property
    def readable_image_formats(self) -> str:
        return ", ".join(self.image_format_list)

    @property
    def max_source_size(self) -> int:
        return self.source_sizelimit

    @property
    def max_entry_size(self) -> int:
        return self.entry_sizelimit

    @property
    def max_image_size(self) -> int:
        return self.MAX_IMAGE_SIZE

    @property
    def readable_max_source_size(self) -> str:
        return sizeformat.size_format(self.max_source_size)

    @property
    def readable_max_entry_size(self) -> str:
        return sizeformat.size_format(self.max_entry_size)

    @property
    def readable_max_image_size(self) -> str:
        return sizeformat.size_format(self.max_image_size)

    @property
    def is_imagefile_required(self) -> bool:
        """Is imagefile *required* for this compo"""
        return self.thumbnail_pref == 0

    @property
    def is_imagefile_allowed(self) -> bool:
        """Is imagefile allowed for this compo"""
        return self.thumbnail_pref in [0, 2]

    @property
    def is_imagefile_copied(self) -> bool:
        """Is imagefile copied from entryfile"""
        return self.thumbnail_pref == 1


def generate_entry_file_path(entry: "Entry", filename: str) -> str:
    return generate_upload_path(filename, settings.MEDIA_COMPO_ENTRIES, entry.name_slug, entry.created_at)


def generate_entry_source_path(entry: "Entry", filename: str) -> str:
    return generate_upload_path(filename, settings.MEDIA_COMPO_SOURCES, entry.name_slug, entry.created_at)


def generate_entry_image_path(entry: "Entry", filename: str) -> str:
    return generate_upload_path(filename, settings.MEDIA_COMPO_IMAGES, entry.name_slug, entry.created_at)


class Entry(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("user"),
        on_delete=models.PROTECT,
    )
    compo = models.ForeignKey(Compo, verbose_name=_("compo"), on_delete=models.PROTECT)
    created_at = models.DateTimeField(_("Created at"), default=timezone.now)
    name = models.CharField(_("Name"), max_length=64)
    description = models.TextField(_("Description"))
    creator = models.CharField(_("Creator"), max_length=64)
    platform = models.CharField(
        _("Platform"),
        max_length=128,
        null=True,
        blank=True,
    )
    entryfile = models.FileField(_("File"), max_length=255, upload_to=generate_entry_file_path)
    sourcefile = models.FileField(
        _("Source code"),
        max_length=255,
        upload_to=generate_entry_source_path,
        blank=True,
    )
    imagefile_original = models.ImageField(
        _("Image"),
        max_length=255,
        upload_to=generate_entry_image_path,
        blank=True,
    )
    imagefile_thumbnail = ImageSpecField(
        [ResizeToFill(160, 100)],
        source="imagefile_original",
        format="JPEG",
        options={"quality": 90},
    )
    imagefile_medium = ImageSpecField(
        [ResizeToFill(640, 400)],
        source="imagefile_original",
        format="JPEG",
        options={"quality": 90},
    )
    youtube_url = YoutubeVideoField(_("Youtube URL"), null=True, blank=True)
    disqualified = models.BooleanField(_("Disqualified"), default=False)
    disqualified_reason = models.TextField(_("Disqualification reason"), blank=True)
    archive_score = models.FloatField(_("Score"), null=True, blank=True)
    archive_rank = models.IntegerField(_("Rank"), null=True, blank=True)

    objects = EntryQuerySet.as_manager()

    # Annotation attributes added by EntryQuerySet.with_score() / with_rank()
    computed_score: float
    computed_rank: int

    def __str__(self) -> str:
        return "{} by {}".format(self.name, self.creator)

    @property
    def entry_file_ext(self) -> str:
        return Path(self.entryfile.name).suffix

    @property
    def archive_embed_url(self) -> str:
        return str(self.youtube_url.embed_obj(autoplay=True))

    @property
    def is_audio(self) -> bool:
        return self.entry_file_ext in AUDIO_FILE_EXTENSIONS

    def get_show_list(self) -> dict[str, bool]:
        show = {"youtube": False, "image": False, "noshow": True}

        state = self.compo.entry_view_type
        if state == 1:
            if self.youtube_url:
                show["youtube"] = True
            elif self.imagefile_original:
                show["image"] = True
        elif state == 2 or state == 3:  # 3 is deprecated
            if self.imagefile_original:
                show["image"] = True

        if show["image"] or show["youtube"]:
            show["noshow"] = False

        return show

    @property
    def name_slug(self) -> str:
        """Generate a normalized entry name (for eg. filenames)"""
        file_pieces = [
            clean_filename(self.creator) if self.creator else None,
            clean_filename(self.name),
        ]
        return "__".join(p for p in file_pieces if p)

    def generate_alternates(self) -> None:
        """Trigger generating additional formats"""
        from Instanssi.kompomaatti import tasks

        if self.is_audio:
            for codec, container in WEB_AUDIO_FORMATS:
                tasks.generate_alternate_audio_files.apply_async(
                    countdown=1, args=[self.id, int(codec), int(container)]
                )

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Save and force regeneration of alternate files"""
        super().save(*args, **kwargs)
        self.generate_alternates()


def generate_entry_alternate_file_path(alt: "AlternateEntryFile", filename: str) -> str:
    return generate_upload_path(
        filename, settings.MEDIA_COMPO_ALTERNATES, alt.entry.name_slug, alt.entry.created_at
    )


class AlternateEntryFile(models.Model):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name="alternate_files")
    codec = models.IntegerField(choices=MediaCodec.choices)
    container = models.IntegerField(choices=MediaContainer.choices)
    file = models.FileField(max_length=255, upload_to=generate_entry_alternate_file_path)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    @property
    def codec_name(self) -> str:
        return MediaCodec(self.codec).name.lower()

    @property
    def container_name(self) -> str:
        return MediaContainer(self.container).name.lower()

    @property
    def mime_format(self) -> str:
        return f"audio/{self.container_name};codecs={self.codec_name}"

    def __str__(self) -> str:
        return f"Alternate {self.codec_name}/{self.container_name} file for {self.entry.name}"


class VoteGroup(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("user"), on_delete=models.CASCADE)
    compo = models.ForeignKey(Compo, verbose_name=_("compo"), on_delete=models.CASCADE)

    @property
    def entries(self) -> list[Entry]:
        return [v.entry for v in self.votes.order_by("rank")]

    def delete_votes(self) -> None:
        Vote.objects.filter(group=self).delete()

    def create_votes(self, entries: Iterable[Entry]) -> None:
        current_rank = 1
        for entry in entries:
            Vote(user=self.user, compo=self.compo, rank=current_rank, entry=entry, group=self).save()
            current_rank += 1

    def __str__(self) -> str:
        return "votes for {} by {}".format(self.compo.name, self.user.username)

    class Meta:
        unique_together = (("user", "compo"),)


class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("user"), on_delete=models.CASCADE)
    compo = models.ForeignKey(Compo, verbose_name=_("compo"), on_delete=models.CASCADE)
    entry = models.ForeignKey(Entry, verbose_name=_("entry"), on_delete=models.CASCADE)
    rank = models.IntegerField(_("Rank"))
    group = models.ForeignKey(
        VoteGroup,
        default=None,
        null=True,
        blank=True,
        related_name="votes",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return "{} by {} as {}".format(self.entry.name, self.user.username, self.rank)


class Competition(models.Model):
    ENTRY_VIEW_TYPES = (
        (0, _("Highest score first")),
        (1, _("Lowest score first")),
    )

    event = models.ForeignKey(
        Event,
        verbose_name=_("Event"),
        on_delete=models.PROTECT,
    )
    name = models.CharField(_("Name"), max_length=32)
    description = SanitizedHtmlField(_("Description"))
    participation_end = models.DateTimeField(_("Participation deadline"))
    start = models.DateTimeField(_("Competition start"), db_index=True)
    end = models.DateTimeField(_("Competition end"), null=True, blank=True)
    score_type = models.CharField(_("Score type"), max_length=8)
    score_sort = models.IntegerField(
        _("Score sorting"),
        choices=ENTRY_VIEW_TYPES,
        default=0,
    )
    show_results = models.BooleanField(_("Show results"), default=False)
    active = models.BooleanField(_("Active"), default=True)
    hide_from_archive = models.BooleanField(_("Hide from archive"), default=False)

    def is_participating_open(self) -> bool:
        return timezone.now() < self.participation_end

    def __str__(self) -> str:
        return "{}: {}".format(self.event.name, self.name)


class CompetitionParticipation(models.Model):
    computed_rank: int  # Set by with_rank() annotation

    competition = models.ForeignKey(
        Competition,
        verbose_name=_("Competition"),
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
    )
    participant_name = models.CharField(
        _("Participant name"),
        max_length=32,
        default="",
    )
    score = models.FloatField(_("Score"), blank=True, default=0)
    disqualified = models.BooleanField(_("Disqualified"), default=False)
    disqualified_reason = models.TextField(_("Disqualification reason"), blank=True)

    objects = CompetitionParticipationQuerySet.as_manager()

    def get_formatted_score(self) -> str:
        return "{} {}".format(self.score, self.competition.score_type)

    def get_rank(self) -> int:
        # Get results
        rank_by = "-score"
        if self.competition.score_sort == 1:
            rank_by = "score"
        results = CompetitionParticipation.objects.filter(competition_id=self.competition.id).order_by(
            rank_by
        )

        # Find self
        rank = 1
        for p in results:
            if p.id == self.id:
                return rank
            else:
                rank += 1
        return rank

    def __str__(self) -> str:
        return "{}, {}: {}".format(self.competition.name, self.participant_name, self.score)


auditlog.register(Compo)
auditlog.register(Competition)
auditlog.register(Entry)
auditlog.register(CompetitionParticipation)
auditlog.register(Vote)
auditlog.register(VoteGroup)
auditlog.register(VoteCodeRequest)
auditlog.register(Event)
auditlog.register(TicketVoteCode)
auditlog.register(AlternateEntryFile)
