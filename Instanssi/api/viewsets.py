# -*- coding: utf-8 -*-

from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, ListModelMixin

from .serializers import EventSerializer, SongSerializer, CompetitionSerializer
from Instanssi.kompomaatti.models import Event, Competition, Compo
from Instanssi.ext_programme.models import ProgrammeEvent
from Instanssi.screenshow.models import NPSong, Sponsor, Message, IRCMessage


class FilterMixin(object):
    @staticmethod
    def filter_by_event_id(queryset, request):
        event_id = request.query_params.get('event_id', None)
        return queryset.filter(event_id=event_id) if event_id else queryset

    @staticmethod
    def filter_by_lim_off(queryset, request):
        limit = int(request.query_params.get('limit', 100))
        offset = int(request.query_params.get('offset', 0))
        return queryset[offset:offset+limit]


class EventViewSet(ReadOnlyModelViewSet):
    """
    Exposes all Instanssi events
    """
    queryset = Event.objects.filter(name__startswith='Instanssi')
    serializer_class = EventSerializer


class SongViewSet(ReadOnlyModelViewSet, FilterMixin):
    """
    Exposes all Instanssi songs on playlist.

    State:
    0: Playing
    1: Stopped

    Allows GET filters:
    * limit: Limit amount of returned objects. Default is 100.
    * offset: Starting offset. Default is 0.
    * event_id: Filter by event id
    """
    serializer_class = SongSerializer

    def get_queryset(self):
        q = NPSong.objects.all()
        q = self.filter_by_event_id(q, self.request)
        q = self.filter_by_lim_off(q, self.request)
        return q

    def create(self, request):
        pass


class CompetitionViewSet(ReadOnlyModelViewSet, FilterMixin):
    """
    Exposes all sports competitions.

    Score_sort:
    0: Highest score first
    1: Lowest score first

    Allows GET filters:
    * limit: Limit amount of returned objects. Default is 100.
    * offset: Starting offset. Default is 0.
    * event_id: Filter by event id
    """
    serializer_class = CompetitionSerializer

    def get_queryset(self):
        q = Competition.objects.filter(active=True)
        q = self.filter_by_event_id(q, self.request)
        q = self.filter_by_lim_off(q, self.request)
        return q

