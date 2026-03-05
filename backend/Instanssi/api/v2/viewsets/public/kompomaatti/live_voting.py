from django.http import Http404
from django.utils.http import http_date, parse_http_date_safe
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from Instanssi.kompomaatti.models import Compo, Entry, LiveVotingState


class PublicLiveVotingView(APIView):
    """Public polling endpoint for live voting state.

    Returns the current live voting state for a compo, including which entries
    have been revealed. Supports conditional requests via If-Modified-Since
    for efficient polling.
    """

    permission_classes = [AllowAny]
    authentication_classes: list[type] = []

    @extend_schema(
        responses={
            200: inline_serializer(
                name="PublicLiveVotingState",
                fields={
                    "compo": serializers.IntegerField(),
                    "voting_open": serializers.BooleanField(),
                    "current_entry": serializers.IntegerField(allow_null=True),
                    "updated_at": serializers.DateTimeField(),
                    "revealed_entries": serializers.ListField(child=serializers.IntegerField()),
                },
            ),
            304: None,
            404: None,
        }
    )
    def get(self, request: Request, event_pk: int, compo_pk: int) -> Response:
        try:
            compo = Compo.objects.get(
                pk=compo_pk,
                event_id=event_pk,
                event__hidden=False,
                active=True,
            )
        except Compo.DoesNotExist:
            raise Http404

        try:
            state = compo.live_voting_state
        except LiveVotingState.DoesNotExist:
            raise Http404

        # Check If-Modified-Since for polling efficiency
        ims = request.META.get("HTTP_IF_MODIFIED_SINCE")
        if ims:
            ims_timestamp = parse_http_date_safe(ims)
            if ims_timestamp is not None:
                state_timestamp = int(state.updated_at.timestamp())
                if state_timestamp <= ims_timestamp:
                    return Response(status=304)

        revealed_entry_ids = list(
            Entry.objects.filter(compo=compo, live_voting_revealed=True)
            .order_by("live_voting_order")
            .values_list("id", flat=True)
        )

        data = {
            "compo": compo.pk,
            "voting_open": state.voting_open,
            "current_entry": state.current_entry_id,
            "updated_at": state.updated_at.isoformat(),
            "revealed_entries": revealed_entry_ids,
        }

        response = Response(data)
        response["Last-Modified"] = http_date(state.updated_at.timestamp())
        return response
