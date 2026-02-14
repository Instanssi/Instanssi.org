import logging

from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from Instanssi.api.v1.serializers.kompomaatti import (
    CompetitionParticipationSerializer,
    CompetitionSerializer,
    CompoEntrySerializer,
    CompoSerializer,
    EventSerializer,
    TicketVoteCodeSerializer,
    UserCompetitionParticipationSerializer,
    UserCompoEntrySerializer,
    VoteCodeRequestSerializer,
    VoteGroupSerializer,
)
from Instanssi.api.v1.utils import ReadWriteModelViewSet, ReadWriteUpdateModelViewSet
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
from Instanssi.notifications.tasks import notify_new_vote_code_request

logger = logging.getLogger(__name__)


class EventViewSet(ReadOnlyModelViewSet):
    """
    Exposes all Instanssi events. Note that ID's assigned to events are guaranteed to stay the same; they will not
    change, ever. So if you want, you can hardcode the event id's in your own code and don't need to bother fetching
    this data.

    Allows GET filters:
    * limit: Limit amount of returned objects.
    * offset: Starting offset. Default is 0.
    * event: Filter by event id
    * ordering: Set ordering, default is 'id'. Allowed: id, -id
    """

    queryset = Event.objects.filter(hidden=False)
    serializer_class = EventSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (
        OrderingFilter,
        DjangoFilterBackend,
    )
    ordering_fields = ("id",)
    filterset_fields = ("id",)


class CompetitionViewSet(ReadOnlyModelViewSet):
    """
    Exposes all sports competitions.

    Score_sort:
    0: Highest score first
    1: Lowest score first

    Allows GET filters:
    * limit: Limit amount of returned objects.
    * offset: Starting offset. Default is 0.
    * event: Filter by event id
    * ordering: Set ordering, default is 'id'. Allowed: id, -id
    """

    queryset = Competition.objects.filter(active=True, event__hidden=False)
    serializer_class = CompetitionSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (
        OrderingFilter,
        DjangoFilterBackend,
    )
    ordering_fields = ("id",)
    filterset_fields = ("event",)


class CompetitionParticipationViewSet(ReadOnlyModelViewSet):
    """
    Exposes all competition participations. This is everything that does not drop neatly to the democompo category,
    eg. sports events etc.

    Allows GET filters:
    * limit: Limit amount of returned objects.
    * offset: Starting offset. Default is 0.
    * competition: Filter by competition id
    * ordering: Set ordering, default is 'id'. Allowed: id, -id
    """

    queryset = CompetitionParticipation.objects.filter(
        competition__active=True, competition__event__hidden=False
    )
    serializer_class = CompetitionParticipationSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (
        OrderingFilter,
        DjangoFilterBackend,
    )
    ordering_fields = ("id",)
    filterset_fields = ("competition",)


class UserCompetitionParticipationViewSet(ModelViewSet):
    """
    Exposes only competition participations that belong to the logged user.

    Allows GET filters:
    * limit: Limit amount of returned objects.
    * offset: Starting offset. Default is 0.
    * competition: Filter by compo id
    * ordering: Set ordering, default is 'id'. Allowed: id, -id
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserCompetitionParticipationSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (
        OrderingFilter,
        DjangoFilterBackend,
    )
    ordering_fields = ("id",)
    filterset_fields = ("competition",)

    def get_queryset(self):
        return CompetitionParticipation.objects.filter(
            competition__active=True, competition__event__hidden=False, user=self.request.user
        )

    def perform_destroy(self, instance):
        if not instance.competition.is_participating_open():
            raise serializers.ValidationError("Osallistuminen on päättynyt")
        return super(UserCompetitionParticipationViewSet, self).perform_destroy(instance)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CompoViewSet(ReadOnlyModelViewSet):
    """
    Exposes all compos.

    Allows GET filters:
    * limit: Limit amount of returned objects.
    * offset: Starting offset. Default is 0.
    * event: Filter by event id
    * ordering: Set ordering, default is 'id'. Allowed: id, -id
    """

    queryset = Compo.objects.filter(active=True, event__hidden=False)
    serializer_class = CompoSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (
        OrderingFilter,
        DjangoFilterBackend,
    )
    ordering_fields = ("id",)
    filterset_fields = ("event",)


class CompoEntryViewSet(ReadOnlyModelViewSet):
    """
    Exposes all compo entries.

    Allows GET filters:
    * limit: Limit amount of returned objects.
    * offset: Starting offset. Default is 0.
    * compo: Filter by compo id
    * ordering: Set ordering, default is 'id'. Allowed: id, -id
    """

    serializer_class = CompoEntrySerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (
        OrderingFilter,
        DjangoFilterBackend,
    )
    ordering_fields = ("id",)
    filterset_fields = ("compo",)

    def get_queryset(self):
        return (
            Entry.objects.filter(compo__active=True, compo__event__hidden=False)
            .filter(Q(compo__voting_start__lt=timezone.now()) | Q(compo__event__archived=True))
            .with_rank()
        )


class UserCompoEntryViewSet(ModelViewSet):
    """
    Exposes only compo entries that belong to the logged user.

    Allows GET filters:
    * limit: Limit amount of returned objects.
    * offset: Starting offset. Default is 0.
    * compo: Filter by compo id
    * ordering: Set ordering, default is 'id'. Allowed: id, -id
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserCompoEntrySerializer
    parser_classes = (
        MultiPartParser,
        FormParser,
    )
    pagination_class = LimitOffsetPagination
    filter_backends = (
        OrderingFilter,
        DjangoFilterBackend,
    )
    ordering_fields = ("id",)
    filterset_fields = ("compo",)

    def get_queryset(self):
        return Entry.objects.filter(compo__active=True, compo__event__hidden=False, user=self.request.user)

    def perform_destroy(self, instance):
        if not instance.compo.is_editing_open():
            raise serializers.ValidationError("Kompon muokkausaika on päättynyt")
        return super(UserCompoEntryViewSet, self).perform_destroy(instance)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        delete_imagefile = False
        delete_sourcefile = False

        # Remove imagefile if requested (field is null)
        if (
            instance.imagefile_original is not None
            and "imagefile_original" in request.data
            and len(request.data["imagefile_original"]) == 0
        ):
            delete_imagefile = True

        # remove sourcefile if requested (field is null)
        if (
            instance.sourcefile is not None
            and "sourcefile" in request.data
            and len(request.data["sourcefile"]) == 0
        ):
            delete_sourcefile = True

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        if delete_imagefile:
            instance.imagefile_original = None
        if delete_sourcefile:
            instance.sourcefile = None

        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class VoteCodeRequestViewSet(ReadWriteUpdateModelViewSet):
    """
    Exposes vote code requests belonging to the currently logged in user.

    Status field has following meanings:
    0 = Pending
    1 = Accepted (voting right granted)
    2 = Rejected (no voting right)

    Allows GET filters:
    * limit: Limit amount of returned objects.
    * offset: Starting offset. Default is 0.
    * event: Filter by event id
    * ordering: Set ordering, default is 'id'. Allowed: id, -id
    """

    permission_classes = [IsAuthenticated]
    serializer_class = VoteCodeRequestSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (
        OrderingFilter,
        DjangoFilterBackend,
    )
    ordering_fields = ("id",)
    filterset_fields = ("event",)

    def get_queryset(self):
        return VoteCodeRequest.objects.filter(user=self.request.user, event__hidden=False)

    def perform_create(self, serializer):
        instance = serializer.save(user=self.request.user)
        notify_new_vote_code_request.delay(instance.id)


class TicketVoteCodeViewSet(ReadWriteModelViewSet):
    """
    Exposes vote codes belonging to the currently logged in user.

    Allows GET filters:
    * limit: Limit amount of returned objects.
    * offset: Starting offset. Default is 0.
    * event: Filter by event id
    * ordering: Set ordering, default is 'id'. Allowed: id, -id
    """

    permission_classes = [IsAuthenticated]
    serializer_class = TicketVoteCodeSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (
        OrderingFilter,
        DjangoFilterBackend,
    )
    ordering_fields = ("id",)
    filterset_fields = ("event",)

    def get_queryset(self):
        return TicketVoteCode.objects.filter(associated_to=self.request.user, event__hidden=False)

    def perform_create(self, serializer):
        serializer.save(associated_to=self.request.user)


class VoteGroupViewSet(ReadWriteModelViewSet):
    """
    Exposes compo entry votes belonging to the currently logged in user.

    Allows GET filters:
    * limit: Limit amount of returned objects.
    * offset: Starting offset. Default is 0.
    * compo: Filter by compo id
    * ordering: Set ordering. Allowed: compo, -compo
    """

    permission_classes = [IsAuthenticated]
    serializer_class = VoteGroupSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (
        OrderingFilter,
        DjangoFilterBackend,
    )
    ordering_fields = ("compo",)
    filterset_fields = ("compo",)

    def get_queryset(self):
        return VoteGroup.objects.filter(user=self.request.user, compo__event__hidden=False)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
