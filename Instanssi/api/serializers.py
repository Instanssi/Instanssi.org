# -*- coding: utf-8 -*-

import logging
import os

from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.serializers import SerializerMethodField, Serializer, EmailField,\
    CharField, IntegerField, ChoiceField, BooleanField, ValidationError, ModelSerializer,\
    ListField, PrimaryKeyRelatedField

from Instanssi.store.methods import PaymentMethod
from Instanssi.store.handlers import validate_item, validate_payment_method, create_store_transaction, \
    TransactionException
from Instanssi.kompomaatti.models import Event, Competition, Compo, Entry, CompetitionParticipation, TicketVoteCode, \
    VoteCodeRequest, VoteGroup
from Instanssi.ext_programme.models import ProgrammeEvent
from Instanssi.screenshow.models import NPSong, Sponsor, Message, IRCMessage
from Instanssi.store.models import StoreItem, StoreItemVariant, TransactionItem
from .mixins import CompoEntrySerializerMixin

logger = logging.getLogger(__name__)


class CompoForeignKey(PrimaryKeyRelatedField):
    def get_queryset(self):
        return Compo.objects.filter(active=True, event__name__startswith='Instanssi')


class CompetitionForeignKey(PrimaryKeyRelatedField):
    def get_queryset(self):
        return Competition.objects.filter(active=True, event__name__startswith='Instanssi')


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email')


class EventSerializer(ModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'name', 'date', 'mainurl')


class CompetitionSerializer(ModelSerializer):
    class Meta:
        model = Competition
        fields = ('id', 'event', 'name', 'description', 'participation_end', 'start', 'end', 'score_type',
                  'score_sort', 'show_results')
        extra_kwargs = {}


class CompetitionParticipationSerializer(ModelSerializer):
    rank = SerializerMethodField()
    score = SerializerMethodField()
    disqualified = SerializerMethodField()
    disqualified_reason = SerializerMethodField()

    def get_disqualified_reason(self, obj):
        if obj.competition.show_results:
            return obj.disqualified_reason
        return None

    def get_disqualified(self, obj):
        if obj.competition.show_results:
            return obj.disqualified
        return None

    def get_rank(self, obj):
        if obj.competition.show_results:
            return obj.get_rank()
        return None

    def get_score(self, obj):
        if obj.competition.show_results:
            return obj.get_formatted_score()
        return None

    class Meta:
        model = CompetitionParticipation
        fields = ('id', 'competition', 'participant_name', 'score', 'rank', 'disqualified', 'disqualified_reason')
        extra_kwargs = {}


class CompoSerializer(ModelSerializer):
    class Meta:
        model = Compo
        fields = ('id', 'event', 'name', 'description', 'adding_end', 'editing_end', 'compo_start', 'voting_start',
                  'voting_end', 'max_source_size', 'max_entry_size', 'max_image_size', 'source_format_list',
                  'entry_format_list', 'image_format_list', 'show_voting_results', 'entry_view_type', 'is_votable',
                  'is_imagefile_allowed', 'is_imagefile_required')
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

    def get_entryfile_url(self, obj):
        if obj.entryfile and (obj.compo.show_voting_results or obj.compo.has_voting_started):
            return self.context['request'].build_absolute_uri(obj.entryfile.url)
        return None

    def get_sourcefile_url(self, obj):
        if obj.sourcefile and (obj.compo.show_voting_results or obj.compo.has_voting_started):
            return self.context['request'].build_absolute_uri(obj.sourcefile.url)
        return None

    def get_imagefile_original_url(self, obj):
        if obj.imagefile_original:
            return self.context['request'].build_absolute_uri(obj.imagefile_original.url)
        return None

    def get_imagefile_medium_url(self, obj):
        if obj.imagefile_medium:
            return self.context['request'].build_absolute_uri(obj.imagefile_medium.url)
        return None

    def get_imagefile_thumbnail_url(self, obj):
        if obj.imagefile_thumbnail:
            return self.context['request'].build_absolute_uri(obj.imagefile_thumbnail.url)
        return None

    def get_disqualified_reason(self, obj):
        if obj.compo.has_voting_started():
            return obj.disqualified_reason
        return None

    def get_disqualified(self, obj):
        if obj.compo.has_voting_started():
            return obj.disqualified
        return None

    def get_rank(self, obj):
        if obj.compo.show_voting_results:
            return obj.get_rank()
        return None

    def get_score(self, obj):
        if obj.compo.show_voting_results:
            return obj.get_score()
        return None

    class Meta:
        model = Entry
        fields = ('id', 'compo', 'name', 'description', 'creator', 'entryfile_url', 'sourcefile_url',
                  'imagefile_original_url', 'imagefile_thumbnail_url', 'imagefile_medium_url', 'youtube_url',
                  'disqualified', 'disqualified_reason', 'score', 'rank')
        extra_kwargs = {}


class UserCompetitionParticipationSerializer(ModelSerializer):
    competition = CompetitionForeignKey()

    def validate_competition(self, competition):
        if not competition.active:
            raise ValidationError("Kilpailu ei ole aktiivinen")
        return competition

    def validate(self, data):
        competition = data.get('competition') or self.instance.competition

        # Check competition edits and additions
        if not competition.is_participating_open():
            raise ValidationError("Kilpailun osallistumisaika on päättynyt")

        data = super(UserCompetitionParticipationSerializer, self).validate(data)

        has_changed = self.instance and self.instance.competition.id != competition.id
        if not self.instance or has_changed:
            obj = CompetitionParticipation.objects.filter(
                competition=competition, user=self.context['request'].user).first()
            if obj:
                raise ValidationError("Olet jo osallistunut tähän kilpailuun")
        return data

    class Meta:
        model = CompetitionParticipation
        fields = ('id', 'competition', 'participant_name')
        extra_kwargs = {
            'id': {'read_only': True},
        }


class UserCompoEntrySerializer(ModelSerializer, CompoEntrySerializerMixin):
    compo = CompoForeignKey()
    entryfile_url = SerializerMethodField()
    sourcefile_url = SerializerMethodField()
    imagefile_original_url = SerializerMethodField()
    imagefile_thumbnail_url = SerializerMethodField()
    imagefile_medium_url = SerializerMethodField()

    def get_entryfile_url(self, obj):
        if obj.entryfile and (obj.compo.show_voting_results or obj.compo.has_voting_started):
            return self.context['request'].build_absolute_uri(obj.entryfile.url)
        return None

    def get_sourcefile_url(self, obj):
        if obj.sourcefile and (obj.compo.show_voting_results or obj.compo.has_voting_started):
            return self.context['request'].build_absolute_uri(obj.sourcefile.url)
        return None

    def get_imagefile_original_url(self, obj):
        if obj.imagefile_original:
            return self.context['request'].build_absolute_uri(obj.imagefile_original.url)
        return None

    def get_imagefile_medium_url(self, obj):
        if obj.imagefile_medium:
            return self.context['request'].build_absolute_uri(obj.imagefile_medium.url)
        return None

    def get_imagefile_thumbnail_url(self, obj):
        if obj.imagefile_thumbnail:
            return self.context['request'].build_absolute_uri(obj.imagefile_thumbnail.url)
        return None

    def validate_compo(self, compo):
        if not compo.active:
            raise ValidationError("Kompoa ei ole olemassa")
        return compo

    def _validate_file(self, file, accept_formats, accept_formats_readable, max_size, max_readable_size):
        errors = []

        # Make sure the file size is within limits
        if file.size > max_size:
            errors.append("Maksimi sallittu tiedostokoko on {}".format(max_readable_size))

        # Make sure the file extension seems correct
        ext = os.path.splitext(file.name)[1][1:]
        if ext not in accept_formats:
            errors.append("Sallitut tiedostotyypit ovat {}".format(accept_formats_readable))

        return errors

    def validate(self, data):
        data = super(UserCompoEntrySerializer, self).validate(data)
        compo = data.get('compo') or self.instance.compo

        # Check adding & editing time
        if not self.instance and not compo.is_adding_open():
            raise ValidationError("Kompon lisäysaika on päättynyt")
        if self.instance and not compo.is_editing_open():
            raise ValidationError("Kompon muokkausaika on päättynyt")

        # Validate imagefile
        self.validate_imagefile(data, compo)

        # Required validation function arguments for each field
        errors = {}
        check_files_on = {
            'entryfile': (
                 compo.entry_format_list, compo.readable_entry_formats,
                 compo.max_entry_size, compo.readable_max_entry_size
            ),
            'sourcefile': (
                 compo.source_format_list, compo.readable_source_formats,
                 compo.max_source_size, compo.readable_max_source_size
            ),
            'imagefile_original': (
                 compo.image_format_list, compo.readable_image_formats,
                 compo.max_image_size, compo.readable_max_image_size
            )
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

    def create(self, validated_data):
        instance = super(UserCompoEntrySerializer, self).create(validated_data)
        self._maybe_copy_entry_to_image(instance)
        return instance

    def update(self, instance, validated_data):
        instance = super(UserCompoEntrySerializer, self).update(instance, validated_data)
        self._maybe_copy_entry_to_image(instance)
        return instance

    class Meta:
        model = Entry
        fields = ('id', 'compo', 'name', 'description', 'creator', 'entryfile', 'imagefile_original', 'sourcefile',
                  'entryfile_url', 'sourcefile_url', 'imagefile_original_url', 'imagefile_thumbnail_url',
                  'imagefile_medium_url', 'disqualified', 'disqualified_reason',)
        extra_kwargs = {
            'id': {'read_only': True},
            'entryfile_url': {'read_only': True},
            'sourcefile_url': {'read_only': True},
            'imagefile_original_url': {'read_only': True},
            'imagefile_thumbnail_url': {'read_only': True},
            'imagefile_medium_url': {'read_only': True},
            'disqualified': {'read_only': True},
            'disqualified_reason': {'read_only': True},
            'entryfile': {'write_only': True, 'required': True},
            'sourcefile': {'write_only': True},
            'imagefile_original': {'write_only': True}
        }


class TicketVoteCodeSerializer(ModelSerializer):
    ticket_key = CharField(min_length=8, trim_whitespace=True, source='key')

    def validate(self, data):
        data = super(TicketVoteCodeSerializer, self).validate(data)

        obj = TicketVoteCode.objects.filter(event=data['event'],
                                            associated_to=self.context['request'].user).first()
        if obj:
            raise ValidationError("Äänestyskoodi on jo hankittu")

        # Check if key is already used, return error if it is
        key = data['key']
        try:
            TicketVoteCode.objects.get(event=data['event'], ticket__key__startswith=key)
            raise ValidationError({'ticket_key': ['Lippuavain on jo käytössä!']})
        except TicketVoteCode.DoesNotExist:
            pass

        # Check if key exists at all
        try:
            TransactionItem.objects.get(
                item__event=data['event'],  # Must match event
                item__is_ticket=True,  # Must be ticket
                key__startswith=key,  # Must start with inserted code
                transaction__time_paid__isnull=False)  # Must be paid
        except TransactionItem.DoesNotExist:
            raise ValidationError({'ticket_key': ['Pyydettyä lippuavainta ei ole olemassa!']})

        return data

    @transaction.atomic
    def create(self, validated_data):
        ticket_key = validated_data.pop('key')
        instance = super(TicketVoteCodeSerializer, self).create(validated_data)
        instance.ticket = TransactionItem.objects.get(
            item__event=validated_data['event'],
            item__is_ticket=True,
            key__startswith=ticket_key)
        instance.time = timezone.now()
        instance.save()
        return instance

    class Meta:
        model = TicketVoteCode
        fields = ('id', 'event', 'time', 'ticket_key')
        extra_kwargs = {
            'event': {'required': True},
            'time': {'read_only': True}
        }


class VoteCodeRequestSerializer(ModelSerializer):
    def validate(self, data):
        event = data.get('event')
        if not event:
            event = self.instance.event

        data = super(VoteCodeRequestSerializer, self).validate(data)

        # If content has changed or is new, make sure to test for uniqueness
        has_changed = self.instance and self.instance.event.id != event.id
        if not self.instance or has_changed:
            obj = VoteCodeRequest.objects.filter(
                event=event, user=self.context['request'].user).first()
            if obj:
                raise ValidationError("Äänestyskoodipyyntö on jo olemassa")

        return data

    class Meta:
        model = VoteCodeRequest
        fields = ('id', 'event', 'text', 'status')
        extra_kwargs = {
            'event': {'required': True},
            'text': {'required': True},
            'status': {'read_only': True},
        }


class VoteGroupSerializer(ModelSerializer):
    entries = ListField(
        min_length=1,
        child=PrimaryKeyRelatedField(
            queryset=Entry.objects.filter(
                compo__active=True,
                disqualified=False)))

    def validate_entries(self, entries):
        # Fail if not unique entries
        ids = [entry.id for entry in entries]
        if len(ids) > len(set(ids)):
            raise ValidationError("Voit äänestää entryä vain kerran")
        return entries

    def validate(self, data):
        data = super(VoteGroupSerializer, self).validate(data)
        compo = data['compo']
        entries = data['entries']
        user = self.context['request'].user

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
                raise ValidationError({'entries': ["Entry '{}' ei kuulu kompoon '{}'".format(entry, compo)]})

        return data

    @transaction.atomic
    def create(self, validated_data):
        entries = validated_data.pop('entries')
        compo = validated_data['compo']
        user = validated_data['user']

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
        fields = ('compo', 'entries',)
        extra_kwargs = {
            'compo': {'required': True},
            'entries': {'required': True},
        }


class SongSerializer(ModelSerializer):
    class Meta:
        model = NPSong
        fields = ('id', 'event', 'title', 'artist', 'time', 'state')
        extra_kwargs = {
            'state': {'read_only': True},
            'time': {'read_only': True},
            'id': {'read_only': True},
        }

    def create(self, validated_data):
        # Set old playing songs to stopped
        NPSong.objects.filter(event=validated_data['event'], state=0).update(state=1)

        # Add new song, set state to playing
        song = NPSong(**validated_data)
        song.state = 0
        song.time = timezone.now()
        song.save()
        return song


class ProgrammeEventSerializer(ModelSerializer):
    class Meta:
        model = ProgrammeEvent
        fields = ('id', 'event', 'start', 'end', 'description', 'title', 'presenters', 'presenters_titles',
                  'place')
        extra_kwargs = {}


class SponsorSerializer(ModelSerializer):
    logo_url = SerializerMethodField()
    logo_scaled_url = SerializerMethodField()

    def get_logo_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.logo.url)

    def get_logo_scaled_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.logo_scaled.url)

    class Meta:
        model = Sponsor
        fields = ('id', 'event', 'name', 'logo_url', 'logo_scaled_url')
        extra_kwargs = {}


class MessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'event', 'show_start', 'show_end', 'text')
        extra_kwargs = {}


class IRCMessageSerializer(ModelSerializer):
    class Meta:
        model = IRCMessage
        fields = ('id', 'event', 'date', 'nick', 'message')
        extra_kwargs = {}


class StoreItemVariantSerializer(ModelSerializer):
    class Meta:
        model = StoreItemVariant
        fields = ('id', 'name')


class StoreItemSerializer(ModelSerializer):
    imagefile_original_url = SerializerMethodField()
    imagefile_thumbnail_url = SerializerMethodField()
    discount_factor = SerializerMethodField()
    variants = StoreItemVariantSerializer(many=True)

    def get_imagefile_original_url(self, obj):
        if not obj.imagefile_original:
            return None
        return self.context['request'].build_absolute_uri(obj.imagefile_original.url)

    def get_imagefile_thumbnail_url(self, obj):
        if not obj.imagefile_thumbnail:
            return None
        return self.context['request'].build_absolute_uri(obj.imagefile_thumbnail.url)

    def get_discount_factor(self, obj):
        return obj.get_discount_factor()

    class Meta:
        model = StoreItem
        fields = ('id', 'event', 'name', 'description', 'price', 'max', 'available', 'imagefile_original_url',
                  'imagefile_thumbnail_url', 'max_per_order', 'sort_index', 'discount_amount', 'discount_percentage',
                  'is_discount_available', 'discount_factor', 'num_available', 'variants')
        extra_kwargs = {}


class StoreTransactionItemSerializer(Serializer):
    item_id = IntegerField()
    variant_id = IntegerField(allow_null=True)
    amount = IntegerField(min_value=1)

    def validate(self, data):
        data = super(StoreTransactionItemSerializer, self).validate(data)
        try:
            validate_item(data)
        except TransactionException as e:
            raise ValidationError(str(e))
        return data


class StoreTransactionSerializer(Serializer):
    first_name = CharField(max_length=64)
    last_name = CharField(max_length=64)
    company = CharField(allow_blank=True, max_length=128)
    email = EmailField(max_length=255)
    telephone = CharField(allow_blank=True, max_length=64)
    mobile = CharField(allow_blank=True, max_length=64)
    street = CharField(max_length=128)
    postal_code = CharField(max_length=16)
    city = CharField(max_length=64)
    country = CharField(max_length=2)
    information = CharField(allow_blank=True, max_length=1024)
    payment_method = ChoiceField(choices=[e.value for e in PaymentMethod])
    read_terms = BooleanField()
    discount_key = CharField(allow_blank=True, required=False, max_length=32)
    items = StoreTransactionItemSerializer(many=True, required=True)
    save = BooleanField(default=False)

    def validate_read_terms(self, value):
        if not value:
            raise ValidationError("Käyttöehdot tulee hyväksyä ennen kuin tilausta voidaan jatkaa")
        return value

    def validate_items(self, value):
        if not value:
            raise ValidationError("Ostoskorissa on oltava vähintään yksi tuote")
        serializer = StoreTransactionItemSerializer(data=value, many=True)
        serializer.is_valid(raise_exception=True)
        return value

    def validate(self, data):
        data = super(StoreTransactionSerializer, self).validate(data)
        try:
            validate_payment_method(data['items'], PaymentMethod(data['payment_method']))
        except TransactionException as e:
            raise ValidationError(str(e))
        return data

    def create(self, validated_data):
        return create_store_transaction(validated_data)
