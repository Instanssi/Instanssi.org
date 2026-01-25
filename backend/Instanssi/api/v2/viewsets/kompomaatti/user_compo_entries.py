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

from Instanssi.api.v2.serializers.kompomaatti import UserCompoEntrySerializer
from Instanssi.kompomaatti.models import Compo, Entry

from .entry_viewset_mixin import EntryViewSetMixin


class UserCompoEntryViewSet(EntryViewSetMixin, ModelViewSet[Entry]):
    permission_classes = [IsAuthenticated]
    serializer_class = UserCompoEntrySerializer
    parser_classes = (MultiPartParser, FormParser)
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    ordering_fields = ("id",)
    filterset_fields = ("compo",)

    def get_queryset(self) -> QuerySet[Entry]:
        event_id = int(self.kwargs["event_pk"])
        user: User = self.request.user  # type: ignore[assignment]
        return (
            Entry.objects.filter(compo__event_id=event_id, compo__active=True, user=user)
            .select_related("compo")
            .prefetch_related("alternate_files")
        )

    def validate_compo_belongs_to_event(self, compo: Compo) -> None:
        """Validate that compo belongs to the event in the URL."""
        event_id = int(self.kwargs["event_pk"])
        if compo.event_id != event_id:
            raise serializers.ValidationError({"compo": ["Compo does not belong to this event"]})

    def perform_create(self, serializer: BaseSerializer[Entry]) -> None:
        if compo := serializer.validated_data.get("compo"):
            self.validate_compo_belongs_to_event(compo)

            # Check compo is active and open for adding
            if not compo.active:
                raise serializers.ValidationError({"compo": ["Compo not found or not active"]})

            if not compo.is_adding_open():
                raise serializers.ValidationError({"compo": ["Compo entry adding time has ended"]})

        serializer.save(user=self.request.user)

    def perform_update(self, serializer: BaseSerializer[Entry]) -> None:
        # Check deadline
        instance = serializer.instance
        assert instance is not None  # Always exists in update context
        if not instance.compo.active:
            raise serializers.ValidationError({"compo": ["Compo is not active"]})

        if not instance.compo.is_editing_open():
            raise serializers.ValidationError({"compo": ["Compo edit time has ended"]})

        serializer.save()

    def validate_partial_update(self, instance: Entry) -> None:
        """Check compo is active and editing is open before partial update."""
        if not instance.compo.active:
            raise serializers.ValidationError({"compo": ["Compo is not active"]})

        if not instance.compo.is_editing_open():
            raise serializers.ValidationError({"compo": ["Compo edit time has ended"]})

    def perform_destroy(self, instance: Entry) -> None:
        if not instance.compo.active:
            raise serializers.ValidationError({"compo": ["Compo is not active"]})

        if not instance.compo.is_editing_open():
            raise serializers.ValidationError({"compo": ["Compo edit time has ended"]})

        super().perform_destroy(instance)
