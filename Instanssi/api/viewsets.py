from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from rest_framework import serializers, status
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from Instanssi.ext_programme.models import ProgrammeEvent
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
from Instanssi.screenshow.models import IRCMessage, Message, NPSong, Sponsor
from Instanssi.store.handlers import begin_payment_process
from Instanssi.store.methods import PaymentMethod
from Instanssi.store.models import StoreItem

from .serializers import (
    CompetitionParticipationSerializer,
    CompetitionSerializer,
    CompoEntrySerializer,
    CompoSerializer,
    EventSerializer,
    IRCMessageSerializer,
    MessageSerializer,
    ProgrammeEventSerializer,
    SongSerializer,
    SponsorSerializer,
    StoreItemSerializer,
    StoreTransactionSerializer,
    TicketVoteCodeSerializer,
    UserCompetitionParticipationSerializer,
    UserCompoEntrySerializer,
    UserSerializer,
    VoteCodeRequestSerializer,
    VoteGroupSerializer,
)
from .utils import (
    CanUpdateScreenData,
    IsAuthenticatedOrWriteOnly,
    ReadWriteModelViewSet,
    ReadWriteUpdateModelViewSet,
    WriteOnlyModelViewSet,
)


class CurrentUserViewSet(ReadOnlyModelViewSet):
    """
    Shows data to the authenticated user about self
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        pass

    def list(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


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

    queryset = Event.objects.filter(name__startswith="Instanssi")
    serializer_class = EventSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (
        OrderingFilter,
        DjangoFilterBackend,
    )
    ordering_fields = ("id",)
    filterset_fields = ("id",)


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

    queryset = Competition.objects.filter(active=True)
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

    queryset = CompetitionParticipation.objects.filter(competition__active=True)
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
        return CompetitionParticipation.objects.filter(competition__active=True, user=self.request.user)

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

    queryset = Compo.objects.filter(active=True)
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
        return Entry.objects.filter(compo__active=True).filter(
            Q(compo__voting_start__lt=timezone.now()) | Q(compo__event__archived=True)
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
        return Entry.objects.filter(compo__active=True, user=self.request.user)

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
        return VoteCodeRequest.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


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
        return TicketVoteCode.objects.filter(associated_to=self.request.user)

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
        return VoteGroup.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProgrammeEventViewSet(ReadOnlyModelViewSet):
    """
    Exposes all programme events.

    Allows GET filters:
    * limit: Limit amount of returned objects.
    * offset: Starting offset. Default is 0.
    * event: Filter by event id
    * ordering: Set ordering, default is 'id'. Allowed: id, -id
    """

    queryset = ProgrammeEvent.objects.filter(active=True)
    serializer_class = ProgrammeEventSerializer
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


class StoreItemViewSet(ReadOnlyModelViewSet):
    """
    Exposes all available store items.  This entrypoint does not require authentication/authorization.
    """

    serializer_class = StoreItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = []

    def get_queryset(self):
        return StoreItem.items_visible(secret_key=self.request.query_params.get("secret_key"))


class StoreTransactionViewSet(WriteOnlyModelViewSet):
    """
    Handles saving store transactions. This entrypoint does not require authentication/authorization.
    """

    serializer_class = StoreTransactionSerializer
    permission_classes = [IsAuthenticatedOrWriteOnly]
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if serializer.validated_data["save"]:
                ta = serializer.save()
                payment_method = PaymentMethod(serializer.validated_data["payment_method"])
                response_url = begin_payment_process(payment_method, ta)
                return Response({"url": response_url}, status=status.HTTP_201_CREATED)
            else:
                return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
