import logging

from django_filters.rest_framework import DjangoFilterBackend
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from Instanssi.api.serializers.screenshow import (
    IRCMessageSerializer,
    MessageSerializer,
    SongSerializer,
    SponsorSerializer,
)
from Instanssi.api.utils import CanUpdateScreenData, ReadWriteModelViewSet
from Instanssi.screenshow.models import IRCMessage, Message, NPSong, Sponsor

logger = logging.getLogger(__name__)


class SongViewSet(ReadWriteModelViewSet):
    """
    Exposes all Instanssi songs on playlist. Note that order is order is descending by default.

    State:
    0: Playing
    1: Stopped

    Allows GET filters:
    * limit: Limit amount of returned objects.
    * offset: Starting offset. Default is 0.
    * event: Filter by event id
    * ordering: Set ordering, default is '-id'. Allowed: id, -id
    """

    queryset = NPSong.objects.get_queryset()
    serializer_class = SongSerializer
    permission_classes = [IsAuthenticated, CanUpdateScreenData, TokenHasReadWriteScope]
    pagination_class = LimitOffsetPagination
    filter_backends = (
        OrderingFilter,
        DjangoFilterBackend,
    )
    ordering_fields = ("id",)
    filterset_fields = ("event",)


class SponsorViewSet(ReadOnlyModelViewSet):
    """
    Exposes all sponsors.

    Allows GET filters:
    * limit: Limit amount of returned objects.
    * offset: Starting offset. Default is 0.
    * event: Filter by event id
    * ordering: Set ordering, default is 'id'. Allowed: id, -id
    """

    queryset = Sponsor.objects.get_queryset()
    serializer_class = SponsorSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (
        OrderingFilter,
        DjangoFilterBackend,
    )
    ordering_fields = ("id",)
    filterset_fields = ("event",)


class MessageViewSet(ReadOnlyModelViewSet):
    """
    Exposes all sponsor messages.

    Allows GET filters:
    * limit: Limit amount of returned objects.
    * offset: Starting offset. Default is 0.
    * event: Filter by event id
    * ordering: Set ordering, default is 'id'. Allowed: id, -id
    """

    queryset = Message.objects.get_queryset()
    serializer_class = MessageSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (
        OrderingFilter,
        DjangoFilterBackend,
    )
    ordering_fields = ("id",)
    filterset_fields = ("event",)


class IRCMessageViewSet(ReadOnlyModelViewSet):
    """
    Exposes all saved IRC messages. Note that order is order is descending by default.

    Allows GET filters:
    * limit: Limit amount of returned objects.
    * offset: Starting offset. Default is 0.
    * event: Filter by event id
    * ordering: Set ordering, default is '-id'. Allowed: id, -id
    """

    queryset = IRCMessage.objects.get_queryset()
    serializer_class = IRCMessageSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (
        OrderingFilter,
        DjangoFilterBackend,
    )
    ordering_fields = ("id",)
    filterset_fields = ("event",)
