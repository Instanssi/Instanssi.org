# -*- coding: utf-8 -*-

import logging

from django.utils import timezone
from rest_framework.serializers import HyperlinkedModelSerializer, SerializerMethodField, Serializer, EmailField,\
    CharField, IntegerField, ChoiceField, BooleanField, ValidationError, ModelSerializer

from Instanssi.store.handlers import validate_item, create_store_transaction, TransactionException
from Instanssi.kompomaatti.models import Event, Competition, Compo
from Instanssi.ext_programme.models import ProgrammeEvent
from Instanssi.screenshow.models import NPSong, Sponsor, Message, IRCMessage
from Instanssi.store.models import StoreItem, StoreItemVariant

logger = logging.getLogger(__name__)


class EventSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'name', 'date', 'mainurl')


class CompetitionSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Competition
        fields = ('id', 'event', 'name', 'description', 'participation_end', 'start', 'end', 'score_type',
                  'score_sort')
        extra_kwargs = {
            'event': {'view_name': 'api:events-detail'}
        }


class CompoSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Compo
        fields = ('id', 'event', 'name', 'description', 'adding_end', 'editing_end', 'compo_start', 'voting_start',
                  'voting_end')
        extra_kwargs = {
            'event': {'view_name': 'api:events-detail'}
        }


class SongSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = NPSong
        fields = ('id', 'event', 'title', 'artist', 'time', 'state')
        extra_kwargs = {
            'state': {
                'read_only': True
            },
            'time': {
                'read_only': True
            },
            'id': {
                'read_only': True
            },
            'event': {'view_name': 'api:events-detail'}
        }

    def create(self, validated_data):
        NPSong.objects.filter(event=validated_data['event']).update(state=1)
        song = NPSong(**validated_data)
        song.state = 0
        song.time = timezone.now()
        song.save()
        return song


class ProgrammeEventSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = ProgrammeEvent
        fields = ('id', 'event', 'start', 'end', 'description', 'title', 'presenters', 'presenters_titles',
                  'place')
        extra_kwargs = {
            'event': {'view_name': 'api:events-detail'}
        }


class SponsorSerializer(HyperlinkedModelSerializer):
    logo_url = SerializerMethodField()
    logo_scaled_url = SerializerMethodField()

    def get_logo_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.logo.url)

    def get_logo_scaled_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.logo_scaled.url)

    class Meta:
        model = Sponsor
        fields = ('id', 'event', 'name', 'logo_url', 'logo_scaled_url')
        extra_kwargs = {
            'event': {'view_name': 'api:events-detail'}
        }


class MessageSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'event', 'show_start', 'show_end', 'text')
        extra_kwargs = {
            'event': {'view_name': 'api:events-detail'}
        }


class IRCMessageSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = IRCMessage
        fields = ('id', 'event', 'date', 'nick', 'message')
        extra_kwargs = {
            'event': {'view_name': 'api:events-detail'}
        }


class StoreItemVariantSerializer(ModelSerializer):
    class Meta:
        model = StoreItemVariant
        fields = ('id', 'name')


class StoreItemSerializer(HyperlinkedModelSerializer):
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
        extra_kwargs = {
            'event': {'view_name': 'api:events-detail'}
        }


class StoreTransactionItemSerializer(Serializer):
    item_id = IntegerField()
    variant_id = IntegerField(allow_null=True)
    amount = IntegerField(min_value=1)

    def validate(self, data):
        super(StoreTransactionItemSerializer, self).validate(data)
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
    payment_method = ChoiceField(choices=[0, 1])  # 1 = paytrail, 0 = bitpay
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

    def create(self, validated_data):
        return create_store_transaction(validated_data)

    def update(self, instance, validated_data):
        pass
