from django.db import transaction
from django.db.models import QuerySet
from django.utils.translation import gettext as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers
from rest_framework.filters import OrderingFilter
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import GenericViewSet

from Instanssi.api.v2.serializers.user.kompomaatti.user_vote_group_serializer import (
    UserVoteGroupSerializer,
)
from Instanssi.kompomaatti.models import (
    Compo,
    Entry,
    TicketVoteCode,
    VoteCodeRequest,
    VoteGroup,
)
from Instanssi.users.models import User


class UserVoteGroupViewSet(CreateModelMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet[VoteGroup]):
    """
    API endpoint for managing user's votes.

    Users submit a ranked list of entries to vote for a compo.
    The order of entries in the list determines the ranking (first = highest rank).

    To vote, POST with:
    - compo: The compo ID
    - entries: List of entry IDs in order of preference

    Re-submitting votes for the same compo replaces previous votes.
    Users can only vote if they have voting rights (TicketVoteCode or approved VoteCodeRequest).
    Votes can only be submitted while the compo voting is open.

    Note: Update and delete are not supported. To change votes, simply POST again.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserVoteGroupSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    ordering_fields = ("id", "compo")
    filterset_fields = ("compo",)
    queryset = VoteGroup.objects.all()

    def get_queryset(self) -> QuerySet[VoteGroup]:
        """Return only the current user's vote groups for compos in this event."""
        event_id = int(self.kwargs["event_pk"])
        user: User = self.request.user  # type: ignore[assignment]
        return self.queryset.filter(compo__event_id=event_id, compo__event__hidden=False, user=user)

    def validate_compo_belongs_to_event(self, compo: Compo) -> None:
        """Validate that compo belongs to the event in the URL and event is not hidden."""
        event_id = int(self.kwargs["event_pk"])
        if compo.event_id != event_id:
            raise serializers.ValidationError({"compo": [_("Compo does not belong to this event")]})
        if compo.event.hidden:
            raise serializers.ValidationError({"compo": [_("Compo is not active")]})

    def validate_entries(self, entries: list[Entry], compo: Compo) -> None:
        """Validate that entries are unique, belong to the compo, and are not disqualified."""
        ids = [entry.id for entry in entries]
        if len(ids) > len(set(ids)):
            raise serializers.ValidationError({"entries": [_("You can only vote for each entry once")]})

        for entry in entries:
            if entry.compo_id != compo.id:
                raise serializers.ValidationError(
                    {
                        "entries": [
                            _("Entry '%(entry)s' does not belong to compo '%(compo)s'")
                            % {"entry": entry.name, "compo": compo.name}
                        ]
                    }
                )
            if entry.disqualified:
                raise serializers.ValidationError(
                    {"entries": [_("Entry '%(entry)s' is disqualified") % {"entry": entry.name}]}
                )

    def validate_voting_rights(self, user: User, compo: Compo) -> None:
        """Validate that the user has voting rights for the compo's event."""
        has_ticket_code = TicketVoteCode.objects.filter(associated_to=user, event=compo.event).exists()
        has_approved_request = VoteCodeRequest.objects.filter(
            user=user, event=compo.event, status=1
        ).exists()
        if not has_ticket_code and not has_approved_request:
            raise serializers.ValidationError(
                {"non_field_errors": [_("You do not have voting rights for this event")]}
            )

    @transaction.atomic
    def perform_create(self, serializer: BaseSerializer[VoteGroup]) -> None:
        """Validate and create/replace votes for a compo."""
        compo: Compo = serializer.validated_data["compo"]
        entries: list[Entry] = serializer.validated_data["entries"]
        user: User = self.request.user  # type: ignore[assignment]

        self.validate_compo_belongs_to_event(compo)

        if not compo.active:
            raise serializers.ValidationError({"compo": [_("Compo is not active")]})

        if not compo.is_voting_open():
            raise serializers.ValidationError({"compo": [_("Voting is not open for this compo")]})

        self.validate_voting_rights(user, compo)
        self.validate_entries(entries, compo)

        # Upsert: delete old votes and create new ones
        group = VoteGroup.objects.filter(compo=compo, user=user).first()
        if group:
            group.delete_votes()
        else:
            group = VoteGroup.objects.create(compo=compo, user=user)

        group.create_votes(entries)
        serializer.instance = group
