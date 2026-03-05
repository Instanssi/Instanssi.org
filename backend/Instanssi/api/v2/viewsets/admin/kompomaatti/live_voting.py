from typing import Any

from django.db import transaction
from django.db.models import Max
from django.utils.translation import gettext as _
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from Instanssi.api.v2.serializers.admin.kompomaatti import (
    LiveVotingEntryActionSerializer,
    LiveVotingStateSerializer,
    LiveVotingUpdateSerializer,
)
from Instanssi.api.v2.utils.base import FullDjangoModelPermissions
from Instanssi.kompomaatti.models import Compo, Entry, LiveVotingState


class LiveVotingViewSet(GenericViewSet[LiveVotingState]):
    """Staff viewset for managing live voting state during a compo presentation."""

    permission_classes = [IsAdminUser, FullDjangoModelPermissions]
    serializer_class = LiveVotingStateSerializer
    queryset = LiveVotingState.objects.all()

    def _get_compo(self) -> Compo:
        event_id = int(self.kwargs["event_pk"])
        compo_pk = int(self.kwargs["pk"])
        try:
            compo = Compo.objects.get(pk=compo_pk, event_id=event_id)
        except Compo.DoesNotExist:
            raise NotFound(_("Compo not found."))
        return compo

    def _get_state(self, compo: Compo) -> LiveVotingState:
        state, _ = LiveVotingState.objects.get_or_create(compo=compo)
        return state

    def _serialize_state(self, state: LiveVotingState, request: Request) -> Response:
        serializer = LiveVotingStateSerializer(state, context={"request": request})
        return Response(serializer.data)

    def retrieve(self, request: Request, **kwargs: Any) -> Response:
        compo = self._get_compo()
        state = self._get_state(compo)
        return self._serialize_state(state, request)

    @extend_schema(request=LiveVotingUpdateSerializer, responses={200: LiveVotingStateSerializer})
    @transaction.atomic
    def partial_update(self, request: Request, **kwargs: Any) -> Response:
        compo = self._get_compo()
        state = self._get_state(compo)
        serializer = LiveVotingUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if "voting_open" in serializer.validated_data:
            state.voting_open = serializer.validated_data["voting_open"]
        if "current_entry" in serializer.validated_data:
            entry = serializer.validated_data["current_entry"]
            if entry is not None and entry.compo_id != compo.id:
                raise NotFound(_("Entry does not belong to this compo."))
            state.current_entry = entry

        state.save()
        return self._serialize_state(state, request)

    @extend_schema(request=LiveVotingEntryActionSerializer, responses={200: LiveVotingStateSerializer})
    @action(detail=True, methods=["post"], url_path="reveal_entry")
    @transaction.atomic
    def reveal_entry(self, request: Request, **kwargs: Any) -> Response:
        compo = self._get_compo()
        state = self._get_state(compo)
        serializer = LiveVotingEntryActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            entry = Entry.objects.get(pk=serializer.validated_data["entry_id"], compo=compo)
        except Entry.DoesNotExist:
            raise NotFound(_("Entry not found in this compo."))

        if not entry.live_voting_revealed:
            max_order = Entry.objects.filter(compo=compo, live_voting_revealed=True).aggregate(
                m=Max("live_voting_order")
            )["m"]
            entry.live_voting_order = (max_order or 0) + 1
            entry.live_voting_revealed = True
            Entry.objects.filter(pk=entry.pk).update(
                live_voting_revealed=True,
                live_voting_order=entry.live_voting_order,
            )

        state.current_entry = entry
        state.save()
        return self._serialize_state(state, request)

    @extend_schema(request=LiveVotingEntryActionSerializer, responses={200: LiveVotingStateSerializer})
    @action(detail=True, methods=["post"], url_path="hide_entry")
    @transaction.atomic
    def hide_entry(self, request: Request, **kwargs: Any) -> Response:
        compo = self._get_compo()
        state = self._get_state(compo)
        serializer = LiveVotingEntryActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            entry = Entry.objects.get(pk=serializer.validated_data["entry_id"], compo=compo)
        except Entry.DoesNotExist:
            raise NotFound(_("Entry not found in this compo."))

        Entry.objects.filter(pk=entry.pk).update(live_voting_revealed=False, live_voting_order=0)

        if state.current_entry_id == entry.pk:
            state.current_entry = None
            state.save()

        return self._serialize_state(state, request)

    @extend_schema(request=None, responses={200: LiveVotingStateSerializer})
    @action(detail=True, methods=["post"], url_path="reveal_all")
    @transaction.atomic
    def reveal_all(self, request: Request, **kwargs: Any) -> Response:
        compo = self._get_compo()
        state = self._get_state(compo)

        max_order = (
            Entry.objects.filter(compo=compo, live_voting_revealed=True).aggregate(
                m=Max("live_voting_order")
            )["m"]
            or 0
        )
        order = max_order + 1
        for entry in Entry.objects.filter(compo=compo, live_voting_revealed=False).order_by("id"):
            Entry.objects.filter(pk=entry.pk).update(live_voting_revealed=True, live_voting_order=order)
            order += 1

        return self._serialize_state(state, request)

    @extend_schema(request=None, responses={200: LiveVotingStateSerializer})
    @action(detail=True, methods=["post"], url_path="hide_all")
    @transaction.atomic
    def hide_all(self, request: Request, **kwargs: Any) -> Response:
        compo = self._get_compo()
        state = self._get_state(compo)

        Entry.objects.filter(compo=compo).update(live_voting_revealed=False, live_voting_order=0)
        state.current_entry = None
        state.save()

        return self._serialize_state(state, request)

    @extend_schema(request=None, responses={200: LiveVotingStateSerializer})
    @action(detail=True, methods=["post"])
    @transaction.atomic
    def reset(self, request: Request, **kwargs: Any) -> Response:
        compo = self._get_compo()
        state = self._get_state(compo)

        Entry.objects.filter(compo=compo).update(live_voting_revealed=False, live_voting_order=0)
        state.voting_open = False
        state.current_entry = None
        state.save()

        return self._serialize_state(state, request)
