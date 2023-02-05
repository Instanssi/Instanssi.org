import logging
import os
from typing import List, Optional

from django.contrib.auth.models import User
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone
from rest_framework.serializers import (
    CharField,
    ListField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    SerializerMethodField,
    ValidationError,
)

from Instanssi.kompomaatti.models import (
    Competition,
    CompetitionParticipation,
    Compo,
    Entry,
    Event,
    TicketVoteCode,
    VoteCodeRequest,
    VoteGroup,
)
from Instanssi.store.models import TransactionItem

logger = logging.getLogger(__name__)


class CompoForeignKey(PrimaryKeyRelatedField):
    def get_queryset(self) -> QuerySet:
        return Compo.objects.filter(active=True, event__name__startswith="Instanssi")


class CompetitionForeignKey(PrimaryKeyRelatedField):
    def get_queryset(self) -> QuerySet:
        return Competition.objects.filter(active=True, event__name__startswith="Instanssi")


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email")


class EventSerializer(ModelSerializer):
    class Meta:
        model = Event
        fields = ("id", "name", "date", "mainurl")


class CompetitionSerializer(ModelSerializer):
    class Meta:
        model = Competition
        fields = (
            "id",
            "event",
            "name",
            "description",
            "participation_end",
            "start",
            "end",
            "score_type",
            "score_sort",
            "show_results",
        )
        extra_kwargs = {}


class CompetitionParticipationSerializer(ModelSerializer):
    rank = SerializerMethodField()
    score = SerializerMethodField()
    disqualified = SerializerMethodField()
    disqualified_reason = SerializerMethodField()

    def get_disqualified_reason(self, obj: CompetitionParticipation) -> Optional[str]:
        if obj.competition.show_results:
            return obj.disqualified_reason
        return None

    def get_disqualified(self, obj: CompetitionParticipation) -> Optional[bool]:
        if obj.competition.show_results:
            return obj.disqualified
        return None

    def get_rank(self, obj: CompetitionParticipation) -> Optional[int]:
        if obj.competition.show_results:
            return obj.get_rank()
        return None

    def get_score(self, obj: CompetitionParticipation) -> Optional[str]:
        if obj.competition.show_results:
            return obj.get_formatted_score()
        return None

    class Meta:
        model = CompetitionParticipation
        fields = (
            "id",
            "competition",
            "participant_name",
            "score",
            "rank",
            "disqualified",
            "disqualified_reason",
        )
        extra_kwargs = {}


class CompoSerializer(ModelSerializer):
    class Meta:
        model = Compo
        fields = (
            "id",
            "event",
            "name",
            "description",
            "adding_end",
            "editing_end",
            "compo_start",
            "voting_start",
            "voting_end",
            "max_source_size",
            "max_entry_size",
            "max_image_size",
            "source_format_list",
            "entry_format_list",
            "image_format_list",
            "show_voting_results",
            "entry_view_type",
            "is_votable",
            "is_imagefile_allowed",
            "is_imagefile_required",
        )
        extra_kwargs = {}


class CompoEntrySerializer(ModelSerializer):
    entryfile_url = SerializerMethodField()
    sourcefile_url = SerializerMethodField()
    imagefile_original_url = SerializerMethodField()
    imagefile_thumbnail_url = SerializerMethodField()
    imagefile_medium_url = SerializerMethodField()
    rank = SerializerMethodField()
    score = SerializerMethodField()
    disqualified = SerializerMethodField()
    disqualified_reason = SerializerMethodField()

    def get_entryfile_url(self, obj: Entry) -> Optional[str]:
        if obj.entryfile and (obj.compo.show_voting_results or obj.compo.has_voting_started):
            return self.context["request"].build_absolute_uri(obj.entryfile.url)
        return None

    def get_sourcefile_url(self, obj: Entry) -> Optional[str]:
        if obj.sourcefile and (obj.compo.show_voting_results or obj.compo.has_voting_started):
            return self.context["request"].build_absolute_uri(obj.sourcefile.url)
        return None

    def get_imagefile_original_url(self, obj: Entry) -> Optional[str]:
        if obj.imagefile_original:
            return self.context["request"].build_absolute_uri(obj.imagefile_original.url)
        return None

    def get_imagefile_medium_url(self, obj: Entry) -> Optional[str]:
        if obj.imagefile_medium:
            return self.context["request"].build_absolute_uri(obj.imagefile_medium.url)
        return None

    def get_imagefile_thumbnail_url(self, obj: Entry) -> Optional[str]:
        if obj.imagefile_thumbnail:
            return self.context["request"].build_absolute_uri(obj.imagefile_thumbnail.url)
        return None

    def get_disqualified_reason(self, obj: Entry) -> Optional[str]:
        if obj.compo.has_voting_started():
            return obj.disqualified_reason
        return None

    def get_disqualified(self, obj: Entry) -> Optional[bool]:
        if obj.compo.has_voting_started():
            return obj.disqualified
        return None

    def get_rank(self, obj: Entry) -> Optional[int]:
        if obj.compo.show_voting_results:
            return obj.get_rank()
        return None

    def get_score(self, obj: Entry) -> Optional[float]:
        if obj.compo.show_voting_results:
            return obj.get_score()
        return None

    class Meta:
        model = Entry
        fields = (
            "id",
            "compo",
            "name",
            "description",
            "creator",
            "platform",
            "entryfile_url",
            "sourcefile_url",
            "imagefile_original_url",
            "imagefile_thumbnail_url",
            "imagefile_medium_url",
            "youtube_url",
            "disqualified",
            "disqualified_reason",
            "score",
            "rank",
        )
        extra_kwargs = {}


class UserCompetitionParticipationSerializer(ModelSerializer):
    competition = CompetitionForeignKey()

    def validate_competition(self, competition: Competition) -> Competition:
        if not competition.active:
            raise ValidationError("Kilpailu ei ole aktiivinen")
        return competition

    def validate(self, data: dict) -> dict:
        competition = data.get("competition")
        if not competition:
            competition = self.instance.competition

        # Check competition edits and additions
        if not competition.is_participating_open():
            raise ValidationError("Kilpailun osallistumisaika on päättynyt")

        data = super(UserCompetitionParticipationSerializer, self).validate(data)

        has_changed = self.instance and self.instance.competition.id != competition.id
        if not self.instance or has_changed:
            obj = CompetitionParticipation.objects.filter(
                competition=competition, user=self.context["request"].user
            ).first()
            if obj:
                raise ValidationError("Olet jo osallistunut tähän kilpailuun")
        return data

    class Meta:
        model = CompetitionParticipation
        fields = ("id", "competition", "participant_name")
        extra_kwargs = {
            "id": {"read_only": True},
        }


class UserCompoEntrySerializer(ModelSerializer):
    compo = CompoForeignKey()
    entryfile_url = SerializerMethodField()
    sourcefile_url = SerializerMethodField()
    imagefile_original_url = SerializerMethodField()
    imagefile_thumbnail_url = SerializerMethodField()
    imagefile_medium_url = SerializerMethodField()

    def get_entryfile_url(self, obj: Entry) -> Optional[str]:
        if obj.entryfile and (obj.compo.show_voting_results or obj.compo.has_voting_started):
            return self.context["request"].build_absolute_uri(obj.entryfile.url)
        return None

    def get_sourcefile_url(self, obj: Entry) -> Optional[str]:
        if obj.sourcefile and (obj.compo.show_voting_results or obj.compo.has_voting_started):
            return self.context["request"].build_absolute_uri(obj.sourcefile.url)
        return None

    def get_imagefile_original_url(self, obj: Entry) -> Optional[str]:
        if obj.imagefile_original:
            return self.context["request"].build_absolute_uri(obj.imagefile_original.url)
        return None

    def get_imagefile_medium_url(self, obj: Entry) -> Optional[str]:
        if obj.imagefile_medium:
            return self.context["request"].build_absolute_uri(obj.imagefile_medium.url)
        return None

    def get_imagefile_thumbnail_url(self, obj: Entry) -> Optional[str]:
        if obj.imagefile_thumbnail:
            return self.context["request"].build_absolute_uri(obj.imagefile_thumbnail.url)
        return None

    def validate_compo(self, compo: Compo) -> Compo:
        if not compo.active:
            raise ValidationError("Kompoa ei ole olemassa")
        return compo

    @staticmethod
    def _validate_file(
        file: UploadedFile,
        accept_formats: List[str],
        accept_formats_readable: str,
        max_size: int,
        max_readable_size: int,
    ) -> List[str]:
        errors = []

        # Make sure the file size is within limits
        if file.size > max_size:
            errors.append(f"Maksimi sallittu tiedostokoko on {max_readable_size}")

        # Make sure the file extension seems correct
        ext = os.path.splitext(file.name)[1][1:]
        if ext.lower() not in accept_formats:
            errors.append(f"Sallitut tiedostotyypit ovat {accept_formats_readable}")

        return errors

    def validate(self, data: dict) -> dict:
        data = super(UserCompoEntrySerializer, self).validate(data)
        compo = data.get("compo")
        if not compo:
            compo = self.instance.compo

        # Check adding & editing time
        if not self.instance and not compo.is_adding_open():
            raise ValidationError("Kompon lisäysaika on päättynyt")
        if self.instance and not compo.is_editing_open():
            raise ValidationError("Kompon muokkausaika on päättynyt")

        # Aggro if image field is missing but required
        if not data.get("imagefile_original") and compo.is_imagefile_required:
            raise ValidationError({"imagefile_original": ["Kuvatiedosto tarvitaan tälle kompolle"]})

        # Also aggro if image field is supplied but not allowed
        if data.get("imagefile_original") and not compo.is_imagefile_allowed:
            raise ValidationError({"imagefile_original": ["Kuvatiedostoa ei tarvita tälle kompolle"]})

        # Required validation function arguments for each field
        errors = {}
        check_files_on = {
            "entryfile": (
                compo.entry_format_list,
                compo.readable_entry_formats,
                compo.max_entry_size,
                compo.readable_max_entry_size,
            ),
            "sourcefile": (
                compo.source_format_list,
                compo.readable_source_formats,
                compo.max_source_size,
                compo.readable_max_source_size,
            ),
            "imagefile_original": (
                compo.image_format_list,
                compo.readable_image_formats,
                compo.max_image_size,
                compo.readable_max_image_size,
            ),
        }

        # Validate each file, and aggregate all errors to a nice dict of lists. This way we can return all possible
        # errors at once instead of user having to try again and again.
        for key, args in check_files_on.items():
            file = data.get(key)
            if not file:
                continue
            field_errors = self._validate_file(file, *args)
            if field_errors:
                errors[key] = field_errors
        if errors:
            raise ValidationError(errors)

        return data

    @staticmethod
    def _maybe_copy_entry_to_image(instance: Entry) -> None:
        """If necessary, copy entryfile to imagefile for thumbnail data"""
        if instance.compo.is_imagefile_copied:
            name = str("th_" + os.path.basename(instance.entryfile.name))
            instance.imagefile_original.save(name, instance.entryfile)

    def create(self, validated_data: dict) -> Entry:
        instance = super(UserCompoEntrySerializer, self).create(validated_data)
        self._maybe_copy_entry_to_image(instance)
        return instance

    def update(self, instance: Entry, validated_data: dict) -> Entry:
        instance = super(UserCompoEntrySerializer, self).update(instance, validated_data)
        self._maybe_copy_entry_to_image(instance)
        return instance

    class Meta:
        model = Entry
        fields = (
            "id",
            "compo",
            "name",
            "description",
            "creator",
            "platform",
            "entryfile",
            "imagefile_original",
            "sourcefile",
            "entryfile_url",
            "sourcefile_url",
            "imagefile_original_url",
            "imagefile_thumbnail_url",
            "imagefile_medium_url",
            "disqualified",
            "disqualified_reason",
        )
        extra_kwargs = {
            "id": {"read_only": True},
            "entryfile_url": {"read_only": True},
            "sourcefile_url": {"read_only": True},
            "imagefile_original_url": {"read_only": True},
            "imagefile_thumbnail_url": {"read_only": True},
            "imagefile_medium_url": {"read_only": True},
            "disqualified": {"read_only": True},
            "disqualified_reason": {"read_only": True},
            "entryfile": {"write_only": True, "required": True},
            "sourcefile": {"write_only": True},
            "imagefile_original": {"write_only": True},
        }


class TicketVoteCodeSerializer(ModelSerializer):
    ticket_key = CharField(min_length=8, trim_whitespace=True, source="key")

    def validate(self, data: dict) -> dict:
        data = super(TicketVoteCodeSerializer, self).validate(data)

        obj = TicketVoteCode.objects.filter(
            event=data["event"], associated_to=self.context["request"].user
        ).first()
        if obj:
            raise ValidationError("Äänestyskoodi on jo hankittu")

        # Check if key is already used, return error if it is
        key = data["key"]
        try:
            TicketVoteCode.objects.get(event=data["event"], ticket__key__startswith=key)
            raise ValidationError({"ticket_key": ["Lippuavain on jo käytössä!"]})
        except TicketVoteCode.DoesNotExist:
            pass

        # Check if key exists at all
        try:
            TransactionItem.objects.get(
                item__event=data["event"],  # Must match event
                item__is_ticket=True,  # Must be ticket
                key__startswith=key,  # Must start with inserted code
                transaction__time_paid__isnull=False,
            )  # Must be paid
        except TransactionItem.DoesNotExist:
            raise ValidationError({"ticket_key": ["Pyydettyä lippuavainta ei ole olemassa!"]})

        return data

    @transaction.atomic
    def create(self, validated_data: dict) -> TicketVoteCode:
        ticket_key = validated_data.pop("key")
        instance = super(TicketVoteCodeSerializer, self).create(validated_data)
        instance.ticket = TransactionItem.objects.get(
            item__event=validated_data["event"], item__is_ticket=True, key__startswith=ticket_key
        )
        instance.time = timezone.now()
        instance.save()
        return instance

    class Meta:
        model = TicketVoteCode
        fields = ("id", "event", "time", "ticket_key")
        extra_kwargs = {"event": {"required": True}, "time": {"read_only": True}}


class VoteCodeRequestSerializer(ModelSerializer):
    def validate(self, data: dict) -> dict:
        event = data.get("event")
        if not event:
            event = self.instance.event

        data = super(VoteCodeRequestSerializer, self).validate(data)

        # If content has changed or is new, make sure to test for uniqueness
        has_changed = self.instance and self.instance.event.id != event.id
        if not self.instance or has_changed:
            obj = VoteCodeRequest.objects.filter(event=event, user=self.context["request"].user).first()
            if obj:
                raise ValidationError("Äänestyskoodipyyntö on jo olemassa")

        return data

    class Meta:
        model = VoteCodeRequest
        fields = ("id", "event", "text", "status")
        extra_kwargs = {
            "event": {"required": True},
            "text": {"required": True},
            "status": {"read_only": True},
        }


class VoteGroupSerializer(ModelSerializer):
    entries = ListField(
        min_length=1,
        child=PrimaryKeyRelatedField(queryset=Entry.objects.filter(compo__active=True, disqualified=False)),
    )

    def validate_entries(self, entries: List[Entry]) -> List[Entry]:
        # Fail if not unique entries
        ids = [entry.id for entry in entries]
        if len(ids) > len(set(ids)):
            raise ValidationError("Voit äänestää entryä vain kerran")
        return entries

    def validate(self, data: dict) -> dict:
        data = super(VoteGroupSerializer, self).validate(data)
        compo = data["compo"]
        entries = data["entries"]
        user = self.context["request"].user

        # Make sure compo voting is open
        if not compo.is_voting_open():
            raise ValidationError("Kompon äänestysaika ei ole voimassa")

        # Make sure user has rights to vote
        try:
            TicketVoteCode.objects.get(associated_to=user, event=compo.event)
        except TicketVoteCode.DoesNotExist:
            try:
                VoteCodeRequest.objects.get(user=user, event=compo.event, status=1)
            except VoteCodeRequest.DoesNotExist:
                raise ValidationError("Äänestysoikeus puuttuu")

        # Make sure entries belong to the requested compo
        for entry in entries:
            if entry.compo.id != compo.id:
                raise ValidationError({"entries": ["Entry '{}' ei kuulu kompoon '{}'".format(entry, compo)]})

        return data

    @transaction.atomic
    def create(self, validated_data: dict) -> VoteGroup:
        entries = validated_data.pop("entries")
        compo = validated_data["compo"]
        user = validated_data["user"]

        # Delete old entries (if any) and add new ones
        group = VoteGroup.objects.filter(compo=compo, user=user).first()
        if group:
            group.delete_votes()
        else:
            group = super(VoteGroupSerializer, self).create(validated_data)

        # Add new voted entries
        group.create_votes(entries)

        # That's that. Return the group.
        return group

    class Meta:
        model = VoteGroup
        fields = (
            "compo",
            "entries",
        )
        extra_kwargs = {
            "compo": {"required": True},
            "entries": {"required": True},
        }
