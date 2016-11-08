# -*- coding: utf-8 -*-

from rest_framework.serializers import HyperlinkedModelSerializer

from Instanssi.kompomaatti.models import Event, Competition, Compo
from Instanssi.ext_programme.models import ProgrammeEvent
from Instanssi.screenshow.models import NPSong, Sponsor, Message, IRCMessage


class EventSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'name', 'date', 'mainurl')


class CompetitionSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Competition
        fields = ('id', 'event_id', 'name', 'description', 'participation_end', 'start', 'end', 'score_type',
                  'score_sort')


class CompoSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Compo
        fields = ('id', 'event_id', 'title', 'artist', 'time', 'state')


class SongSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = NPSong
        fields = ('id', 'event_id', 'title', 'artist', 'time', 'state')


class ProgrammeEventSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = ProgrammeEvent
        fields = ('id', 'event_id', 'title', 'artist', 'time', 'state')


class SponsorSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Sponsor
        fields = ('id', 'event_id', 'title', 'artist', 'time', 'state')


class MessageSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'event_id', 'title', 'artist', 'time', 'state')


class IRCMessageSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = IRCMessage
        fields = ('id', 'event_id', 'title', 'artist', 'time', 'state')

