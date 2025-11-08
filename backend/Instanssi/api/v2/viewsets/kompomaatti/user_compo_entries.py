from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from Instanssi.api.v2.serializers.kompomaatti import UserCompoEntrySerializer
from Instanssi.kompomaatti.models import Compo, Entry


class UserCompoEntryViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserCompoEntrySerializer
    parser_classes = (MultiPartParser, FormParser)
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    ordering_fields = ("id",)
    filterset_fields = ("compo",)

    def get_queryset(self):
        event_id = self.kwargs.get("event_pk")
        queryset = Entry.objects.filter(compo__event_id=event_id, compo__active=True, user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        compo_id = serializer.validated_data.get("compo").id
        try:
            compo = Compo.objects.get(id=compo_id, active=True)
        except Compo.DoesNotExist:
            raise serializers.ValidationError("Compo not found or not active")

        if not compo.is_adding_open():
            raise serializers.ValidationError("Compo entry adding time has ended")

        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if not serializer.instance.compo.active:
            raise serializers.ValidationError("Compo is not active")

        if not serializer.instance.compo.is_editing_open():
            raise serializers.ValidationError("Compo edit time has ended")

        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Validate compo state before processing
        if not instance.compo.active:
            raise serializers.ValidationError("Compo is not active")

        if not instance.compo.is_editing_open():
            raise serializers.ValidationError("Compo edit time has ended")

        delete_image_file = False
        delete_source_file = False

        # Remove image file if requested (field is null)
        if (
            instance.imagefile_original is not None
            and "imagefile_original" in request.data
            and len(request.data["imagefile_original"]) == 0
        ):
            delete_image_file = True

        # remove sourcefile if requested (field is null)
        if (
            instance.sourcefile is not None
            and "sourcefile" in request.data
            and len(request.data["sourcefile"]) == 0
        ):
            delete_source_file = True

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        if delete_image_file:
            instance.imagefile_original = None
        if delete_source_file:
            instance.sourcefile = None

        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_destroy(self, instance):
        if not instance.compo.active:
            raise serializers.ValidationError("Compo is not active")

        if not instance.compo.is_editing_open():
            raise serializers.ValidationError("Compo edit time has ended")

        return super(UserCompoEntryViewSet, self).perform_destroy(instance)
