import logging

from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from Instanssi.api.v2.serializers.admin.arkisto import ArchiverStatusSerializer
from Instanssi.arkisto import utils
from Instanssi.kompomaatti.models import (
    CompetitionParticipation,
    Compo,
    Entry,
    Event,
    Vote,
    VoteGroup,
)

logger = logging.getLogger(__name__)


class ArchiverViewSet(ViewSet):
    """ViewSet for archiving event data.

    Provides actions to:
    - Get archiver status for an event
    - Show/hide event in public archive
    - Optimize voting scores (pre-calculate ranks)
    - Remove old vote records
    - Transfer entry/participation rights to archive user
    """

    permission_classes = [IsAuthenticated]

    def get_event(self) -> Event:
        """Get the event from URL kwargs."""
        event_id = int(self.kwargs["event_pk"])
        return get_object_or_404(Event, pk=event_id)

    def get_compos(self, event: Event) -> QuerySet[Compo]:
        """Get compos for the event."""
        return Compo.objects.filter(event=event)

    def _build_status_response(self) -> Response:
        """Build and return the archiver status response."""
        event = self.get_event()
        compos = self.get_compos(event)

        # Check if there are any compo/competition entries not owned by archive user
        try:
            archive_user = User.objects.get(username="arkisto")
            has_non_archived_items = (
                Entry.objects.filter(compo__in=compos).exclude(user=archive_user).exists()
            )
            if not has_non_archived_items:
                has_non_archived_items = (
                    CompetitionParticipation.objects.filter(competition__event=event)
                    .exclude(user=archive_user)
                    .exists()
                )
        except User.DoesNotExist:
            # If archive user doesn't exist, all items are "non-archived"
            has_non_archived_items = (
                Entry.objects.filter(compo__in=compos).exists()
                or CompetitionParticipation.objects.filter(competition__event=event).exists()
            )

        data = {
            "is_archived": event.archived,
            "has_non_archived_items": has_non_archived_items,
            "ongoing_activity": utils.is_event_ongoing(event),
            "votes_unoptimized": utils.is_votes_unoptimized(compos),
            "old_votes_found": Vote.objects.filter(compo__in=compos).exists(),
        }

        serializer = ArchiverStatusSerializer(data)
        return Response(serializer.data)

    @extend_schema(
        responses={200: ArchiverStatusSerializer},
        summary="Get archiver status",
        description="Returns the current archiving status for the event.",
    )
    @action(detail=False, methods=["get"], url_path="status")
    def status(self, request: Request, event_pk: int) -> Response:
        """Get archiver status for the event."""
        return self._build_status_response()

    @extend_schema(
        responses={200: ArchiverStatusSerializer},
        summary="Show event in archive",
        description="Makes the event visible in the public archive.",
    )
    @action(detail=False, methods=["post"])
    def show(self, request: Request, event_pk: int) -> Response:
        """Show event in public archive. Requires kompomaatti.change_event permission."""
        if not request.user.has_perm("kompomaatti.change_event"):
            return Response({"detail": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        event = self.get_event()
        event.archived = True
        event.save()
        logger.info("Event set as visible in archive", extra={"user": request.user, "event": event})
        return self._build_status_response()

    @extend_schema(
        responses={200: ArchiverStatusSerializer},
        summary="Hide event from archive",
        description="Hides the event from the public archive.",
    )
    @action(detail=False, methods=["post"])
    def hide(self, request: Request, event_pk: int) -> Response:
        """Hide event from public archive. Requires kompomaatti.change_event permission."""
        if not request.user.has_perm("kompomaatti.change_event"):
            return Response({"detail": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        event = self.get_event()
        event.archived = False
        event.save()
        logger.info("Event set as hidden in archive", extra={"user": request.user, "event": event})
        return self._build_status_response()

    @extend_schema(
        responses={200: ArchiverStatusSerializer},
        summary="Optimize voting scores",
        description="Pre-calculates and stores entry ranks and scores. Cannot be run while event is ongoing.",
    )
    @action(detail=False, methods=["post"], url_path="optimize-scores")
    def optimize_scores(self, request: Request, event_pk: int) -> Response:
        """Optimize voting scores. Requires kompomaatti.change_entry permission."""
        if not request.user.has_perm("kompomaatti.change_entry"):
            return Response({"detail": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        event = self.get_event()

        # Don't allow this if event is still ongoing
        if utils.is_event_ongoing(event):
            return Response(
                {"detail": "Cannot optimize scores while event is ongoing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Set score and rank to database
        entries = Entry.objects.filter(compo__event=event).with_rank()
        for entry in entries:
            entry.archive_rank = entry.computed_rank
            entry.archive_score = entry.computed_score
            entry.save()

        logger.info("Event scores optimized", extra={"user": request.user, "event": event})
        return self._build_status_response()

    @extend_schema(
        responses={200: ArchiverStatusSerializer},
        summary="Remove old votes",
        description="Deletes vote records after scores have been optimized. Cannot be run while event is ongoing or if scores are not optimized.",
    )
    @action(detail=False, methods=["post"], url_path="remove-old-votes")
    def remove_old_votes(self, request: Request, event_pk: int) -> Response:
        """Remove old vote records. Requires kompomaatti.delete_vote permission."""
        if not request.user.has_perm("kompomaatti.delete_vote"):
            return Response({"detail": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        event = self.get_event()
        compos = self.get_compos(event)

        # Don't proceed if the event is still ongoing
        if utils.is_event_ongoing(event):
            return Response(
                {"detail": "Cannot remove votes while event is ongoing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Don't allow removing votes if votes haven't yet been consolidated
        if utils.is_votes_unoptimized(compos):
            return Response(
                {"detail": "Scores must be optimized before removing votes"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Delete votes belonging to compos in this event
        for group in VoteGroup.objects.filter(compo__in=compos):
            group.delete_votes()
            group.delete()

        logger.info("Event old votes removed", extra={"user": request.user, "event": event})
        return self._build_status_response()

    @extend_schema(
        responses={200: ArchiverStatusSerializer},
        summary="Transfer rights to archive user",
        description="Transfers entry and competition participation ownership to the 'arkisto' user. Cannot be run while event is ongoing.",
    )
    @action(detail=False, methods=["post"], url_path="transfer-rights")
    def transfer_rights(self, request: Request, event_pk: int) -> Response:
        """Transfer rights to archive user. Requires kompomaatti.change_entry permission."""
        if not request.user.has_perm("kompomaatti.change_entry"):
            return Response({"detail": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        event = self.get_event()

        # Don't allow this if event is still ongoing
        if utils.is_event_ongoing(event):
            return Response(
                {"detail": "Cannot transfer rights while event is ongoing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Transfer all user rights on entries and competition participations
        archive_user = get_object_or_404(User, username="arkisto")
        Entry.objects.filter(compo__event=event).update(user=archive_user)
        CompetitionParticipation.objects.filter(competition__event=event).update(user=archive_user)

        logger.info("Event rights transferred", extra={"user": request.user, "event": event})
        return self._build_status_response()
