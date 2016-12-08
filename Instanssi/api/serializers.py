# -*- coding: utf-8 -*-

from datetime import datetime

from rest_framework.serializers import HyperlinkedModelSerializer, SerializerMethodField

from Instanssi.kompomaatti.models import Event, Competition, Compo
from Instanssi.ext_programme.models import ProgrammeEvent
from Instanssi.screenshow.models import NPSong, Sponsor, Message, IRCMessage
from Instanssi.store.models import StoreItem


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
        song.time = datetime.now()
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


class StoreItemSerializer(HyperlinkedModelSerializer):
    imagefile_original_url = SerializerMethodField()
    imagefile_thumbnail_url = SerializerMethodField()
    discount_factor = SerializerMethodField()

    def get_imagefile_original_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.imagefile_original.url)

    def get_imagefile_thumbnail_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.imagefile_thumbnail.url)

    def get_discount_factor(self, obj):
        return obj.get_discount_factor()

    class Meta:
        model = StoreItem
        fields = ('id', 'event', 'name', 'description', 'price', 'max', 'available', 'imagefile_original_url',
                  'imagefile_thumbnail_url', 'max_per_order', 'sort_index', 'discount_amount', 'discount_percentage',
                  'is_discount_available', 'discount_factor', 'num_available')
        extra_kwargs = {
            'event': {'view_name': 'api:events-detail'}
        }
