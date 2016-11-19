# -*- coding: utf-8 -*-

from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.mixins import CreateModelMixin

from .serializers import EventSerializer, SongSerializer, CompetitionSerializer, CompoSerializer,\
    ProgrammeEventSerializer, SponsorSerializer, MessageSerializer, IRCMessageSerializer
from Instanssi.kompomaatti.models import Event, Competition, Compo
from Instanssi.ext_programme.models import ProgrammeEvent
from Instanssi.screenshow.models import NPSong, Sponsor, Message, IRCMessage


class FilterMixin(object):
    @staticmethod
    def filter_by_event(queryset, request):
        event = request.query_params.get('event', None)
        return queryset.filter(event=event) if event else queryset

    @staticmethod
    def filter_by_lim_off(queryset, request):
        limit = int(request.query_params.get('limit', 100))
        offset = int(request.query_params.get('offset', 0))
        return queryset[offset:offset+limit]

    @staticmethod
    def order_by(queryset, request, default='id', whitelist=None):
        if not whitelist:
            whitelist = ['id', '-id']
        order_by = request.query_params.get('order_by', default)
        if order_by not in whitelist:
            return queryset.order_by(default)
        return queryset.order_by(order_by)


class EventViewSet(ReadOnlyModelViewSet, FilterMixin):
    """
    Exposes all Instanssi events. Note that ID's assigned to events are guaranteed to stay the same; they will not
    change, ever. So if you want, you can hardcode the event id's in your own code and don't need to bother fetching
    this data.

    Allows GET filters:
    * limit: Limit amount of returned objects. Default is 100.
    * offset: Starting offset. Default is 0.
    * event: Filter by event id
    * order_by: Set ordering, default is 'id'. Allowed: id, -id
    """
    serializer_class = EventSerializer

    def get_queryset(self):
        q = Event.objects.filter(name__startswith='Instanssi')
        q = self.filter_by_event(q, self.request)
        q = self.order_by(q, self.request)
        q = self.filter_by_lim_off(q, self.request)
        return q


class SongViewSet(ReadOnlyModelViewSet, CreateModelMixin, FilterMixin):
    """
    Exposes all Instanssi songs on playlist. Note that order is order is descending by default.

    State:
    0: Playing
    1: Stopped

    Allows GET filters:
    * limit: Limit amount of returned objects. Default is 100.
    * offset: Starting offset. Default is 0.
    * event: Filter by event id
    * order_by: Set ordering, default is '-id'. Allowed: id, -id
    """
    serializer_class = SongSerializer

    def get_queryset(self):
        q = NPSong.objects.get_queryset()
        q = self.filter_by_event(q, self.request)
        q = self.order_by(q, self.request, default='-id')
        q = self.filter_by_lim_off(q, self.request)
        return q


class CompetitionViewSet(ReadOnlyModelViewSet, FilterMixin):
    """
    Exposes all sports competitions.

    Score_sort:
    0: Highest score first
    1: Lowest score first

    Allows GET filters:
    * limit: Limit amount of returned objects. Default is 100.
    * offset: Starting offset. Default is 0.
    * event: Filter by event id
    * order_by: Set ordering, default is 'id'. Allowed: id, -id
    """
    serializer_class = CompetitionSerializer

    def get_queryset(self):
        q = Competition.objects.filter(active=True)
        q = self.filter_by_event(q, self.request)
        q = self.order_by(q, self.request)
        q = self.filter_by_lim_off(q, self.request)
        return q


class CompoViewSet(ReadOnlyModelViewSet, FilterMixin):
    """
    Exposes all compos.

    Allows GET filters:
    * limit: Limit amount of returned objects. Default is 100.
    * offset: Starting offset. Default is 0.
    * event: Filter by event id
    * order_by: Set ordering, default is 'id'. Allowed: id, -id
    """
    serializer_class = CompoSerializer

    def get_queryset(self):
        q = Compo.objects.filter(active=True)
        q = self.filter_by_event(q, self.request)
        q = self.order_by(q, self.request)
        q = self.filter_by_lim_off(q, self.request)
        return q


class ProgrammeEventViewSet(ReadOnlyModelViewSet, FilterMixin):
    """
    Exposes all programme events.

    Allows GET filters:
    * limit: Limit amount of returned objects. Default is 100.
    * offset: Starting offset. Default is 0.
    * event: Filter by event id
    * order_by: Set ordering, default is 'id'. Allowed: id, -id
    """
    serializer_class = ProgrammeEventSerializer

    def get_queryset(self):
        q = ProgrammeEvent.objects.filter(active=True)
        q = self.filter_by_event(q, self.request)
        q = self.order_by(q, self.request)
        q = self.filter_by_lim_off(q, self.request)
        return q


class SponsorViewSet(ReadOnlyModelViewSet, FilterMixin):
    """
    Exposes all sponsors.

    Allows GET filters:
    * limit: Limit amount of returned objects. Default is 100.
    * offset: Starting offset. Default is 0.
    * event: Filter by event id
    * order_by: Set ordering, default is 'id'. Allowed: id, -id
    """
    serializer_class = SponsorSerializer

    def get_queryset(self):
        q = Sponsor.objects.get_queryset()
        q = self.filter_by_event(q, self.request)
        q = self.order_by(q, self.request)
        q = self.filter_by_lim_off(q, self.request)
        return q


class MessageViewSet(ReadOnlyModelViewSet, FilterMixin):
    """
    Exposes all sponsor messages.

    Allows GET filters:
    * limit: Limit amount of returned objects. Default is 100.
    * offset: Starting offset. Default is 0.
    * event: Filter by event id
    * order_by: Set ordering, default is 'id'. Allowed: id, -id
    """
    serializer_class = MessageSerializer

    def get_queryset(self):
        q = Message.objects.get_queryset()
        q = self.filter_by_event(q, self.request)
        q = self.order_by(q, self.request)
        q = self.filter_by_lim_off(q, self.request)
        return q


class IRCMessageViewSet(ReadOnlyModelViewSet, FilterMixin):
    """
    Exposes all saved IRC messages. Note that order is order is descending by default.

    Allows GET filters:
    * limit: Limit amount of returned objects. Default is 100.
    * offset: Starting offset. Default is 0.
    * event: Filter by event id
    * order_by: Set ordering, default is '-id'. Allowed: id, -id
    """
    serializer_class = IRCMessageSerializer

    def get_queryset(self):
        q = IRCMessage.objects.get_queryset()
        q = self.filter_by_event(q, self.request)
        q = self.order_by(q, self.request, default='-id')
        q = self.filter_by_lim_off(q, self.request)
        return q
