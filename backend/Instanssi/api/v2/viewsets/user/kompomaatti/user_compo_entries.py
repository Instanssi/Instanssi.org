from django.contrib.auth.models import User
from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import ModelViewSet

from Instanssi.api.v2.serializers.user.kompomaatti import UserCompoEntrySerializer
from Instanssi.api.v2.utils.entry_file_validation import (
    maybe_copy_entry_to_image,
    validate_entry_files,
)
from Instanssi.kompomaatti.models import Compo, Entry


class UserCompoEntryViewSet(ModelViewSet[Entry]):
    """Manage the current user's own compo entries.

    Supports ordering by rank and score.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserCompoEntrySerializer
    parser_classes = (MultiPartParser, FormParser)
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    ordering_fields = ("id", "compo", "name", "computed_rank", "computed_score")
    filterset_fields = ("compo",)
    queryset = Entry.objects.all()

    def get_queryset(self) -> QuerySet[Entry]:
        event_id = int(self.kwargs["event_pk"])
        user: User = self.request.user  # type: ignore[assignment]
        return (
            self.queryset.filter(
                compo__event_id=event_id, compo__event__hidden=False, compo__active=True, user=user
            )
            .select_related("compo")
            .prefetch_related("alternate_files")
            .with_rank()
        )

    def validate_compo_belongs_to_event(self, compo: Compo) -> None:
        """Validate that compo belongs to the event in the URL and event is not hidden."""
        event_id = int(self.kwargs["event_pk"])
        if compo.event_id != event_id:
            raise serializers.ValidationError({"compo": ["Compo does not belong to this event"]})
        if compo.event.hidden:
            raise serializers.ValidationError({"compo": ["Compo not found or not active"]})

    def _validate_editing_allowed(self, compo: Compo) -> None:
        """Validate that the compo is active and editing is still open."""
        if not compo.active:
            raise serializers.ValidationError({"compo": ["Compo is not active"]})
        if not compo.is_editing_open():
            raise serializers.ValidationError({"compo": ["Compo edit time has ended"]})

    def _refresh_with_annotations(self, serializer: BaseSerializer[Entry]) -> None:
        """Refresh the serializer instance with score/rank annotations."""
        assert serializer.instance is not None
        serializer.instance = self.get_queryset().get(pk=serializer.instance.pk)

    def perform_create(self, serializer: BaseSerializer[Entry]) -> None:
        if compo := serializer.validated_data.get("compo"):
            self.validate_compo_belongs_to_event(compo)

            if not compo.active:
                raise serializers.ValidationError({"compo": ["Compo not found or not active"]})

            if not compo.is_adding_open():
                raise serializers.ValidationError({"compo": ["Compo entry adding time has ended"]})

            validate_entry_files(serializer.validated_data, compo)

        instance = serializer.save(user=self.request.user)
        maybe_copy_entry_to_image(instance)
        self._refresh_with_annotations(serializer)

    def perform_update(self, serializer: BaseSerializer[Entry]) -> None:
        instance = serializer.instance
        assert instance is not None

        serializer.validated_data.pop("compo", None)
        self._validate_editing_allowed(instance.compo)
        validate_entry_files(serializer.validated_data, instance.compo, instance)
        instance = serializer.save()
        maybe_copy_entry_to_image(instance)
        self._refresh_with_annotations(serializer)

    def validate_partial_update(self, instance: Entry) -> None:
        self._validate_editing_allowed(instance.compo)

    def perform_destroy(self, instance: Entry) -> None:
        self._validate_editing_allowed(instance.compo)
        super().perform_destroy(instance)
