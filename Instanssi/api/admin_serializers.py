# -*- coding: utf-8 -*-

import logging

from django.contrib.auth.models import User, Group
from rest_framework.serializers import ModelSerializer, SerializerMethodField, ListField, IntegerField, CharField

from Instanssi.kompomaatti.models import Event, Compo, Competition, Entry, CompetitionParticipation
from Instanssi.ext_blog.models import BlogEntry

logger = logging.getLogger(__name__)


class AdminEventSerializer(ModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'name', 'date', 'archived', 'mainurl')


class AdminUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined',
                  'is_superuser', 'groups')


class AdminGroupSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')


class AdminCompetitionSerializer(ModelSerializer):
    class Meta:
        model = Competition
        fields = ('id', 'event', 'name', 'description', 'participation_end', 'start', 'end', 'score_type',
                  'score_sort', 'show_results', 'active', 'hide_from_archive')
        extra_kwargs = {}


class AdminCompetitionParticipationSerializer(ModelSerializer):
    rank = SerializerMethodField()

    def get_rank(self, obj):
        if obj.competition.show_results:
            return obj.get_rank()
        return None

    class Meta:
        model = CompetitionParticipation
        fields = ('id', 'competition', 'user', 'participant_name', 'score', 'rank', 'disqualified',
                  'disqualified_reason')
        extra_kwargs = {
            'rank': {'read_only': True},
        }


class AdminCompoSerializer(ModelSerializer):
    max_entry_size = IntegerField()
    max_source_size = IntegerField()
    source_format_list = ListField(child=CharField())
    entry_format_list = ListField(child=CharField())
    image_format_list = ListField(child=CharField())

    class Meta:
        model = Compo
        fields = ('id', 'event', 'name', 'description', 'adding_end', 'editing_end', 'compo_start', 'voting_start',
                  'voting_end', 'max_source_size', 'max_entry_size', 'source_format_list', 'entry_format_list',
                  'image_format_list', 'active', 'show_voting_results', 'entry_view_type', 'hide_from_archive',
                  'hide_from_frontpage', 'is_votable', 'thumbnail_pref')


class AdminCompoEntrySerializer(ModelSerializer):
    entryfile_url = SerializerMethodField()
    sourcefile_url = SerializerMethodField()
    imagefile_original_url = SerializerMethodField()
    imagefile_thumbnail_url = SerializerMethodField()
    imagefile_medium_url = SerializerMethodField()
    rank = SerializerMethodField()
    score = SerializerMethodField()

    def get_entryfile_url(self, obj):
        if obj.entryfile:
            return self.context['request'].build_absolute_uri(obj.entryfile.url)
        return None

    def get_sourcefile_url(self, obj):
        if obj.sourcefile:
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
        fields = ('id', 'user', 'compo', 'name', 'description', 'creator', 'entryfile_url', 'sourcefile_url',
                  'imagefile_original_url', 'imagefile_thumbnail_url', 'imagefile_medium_url', 'youtube_url',
                  'disqualified', 'disqualified_reason', 'score', 'rank', 'archive_score', 'archive_rank')
        extra_kwargs = {
            'entryfile_url': {'read_only': True},
            'sourcefile_url': {'read_only': True},
            'imagefile_original_url': {'read_only': True},
            'imagefile_thumbnail_url': {'read_only': True},
            'imagefile_medium_url': {'read_only': True},
        }


class AdminBlogEntrySerializer(ModelSerializer):
    class Meta:
        model = BlogEntry
        fields = ('id', 'event', 'user', 'title', 'text', 'date', 'public')
