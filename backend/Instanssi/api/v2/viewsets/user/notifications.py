from typing import Any

from django.db.models import QuerySet
from rest_framework import status
from rest_framework.mixins import DestroyModelMixin, ListModelMixin
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from Instanssi.api.v2.serializers.user.notifications import PushSubscriptionSerializer
from Instanssi.notifications.models import PushSubscription
from Instanssi.users.models import User


class UserPushSubscriptionViewSet(DestroyModelMixin, ListModelMixin, GenericViewSet[PushSubscription]):
    """Viewset for managing the current user's push notification subscriptions.

    Supports create (subscribe), destroy (unsubscribe), and list (view subscriptions).
    Subscriptions are scoped to the current user. Create performs upsert by endpoint.
    """

    permission_classes = [IsAdminUser]
    serializer_class = PushSubscriptionSerializer
    queryset = PushSubscription.objects.all()

    def get_queryset(self) -> QuerySet[PushSubscription]:
        user: User = self.request.user  # type: ignore[assignment]
        return self.queryset.filter(user=user)

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Create or update a push subscription (upsert by endpoint).

        A push endpoint is a browser-level resource — the same physical push channel
        regardless of which user subscribed. The lookup uses endpoint alone (matching
        the model's unique constraint) so that if a different user subscribes from the
        same browser, the subscription is reassigned to them rather than creating a
        duplicate that would cause the browser to show the same notification twice.
        """
        serializer = PushSubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user: User = request.user  # type: ignore[assignment]
        obj, _ = PushSubscription.objects.update_or_create(
            endpoint=serializer.validated_data["endpoint"],
            defaults={
                "user": user,
                "p256dh": serializer.validated_data["p256dh"],
                "auth": serializer.validated_data["auth"],
            },
        )
        output = PushSubscriptionSerializer(obj)
        return Response(output.data, status=status.HTTP_201_CREATED)
