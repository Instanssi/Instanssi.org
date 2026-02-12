from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from Instanssi.api.v2.serializers.user import UserInfoSerializer
from Instanssi.users.models import User


class UserInfoViewSet(GenericViewSet[User]):
    """Retrieve and update the current authenticated user's profile and permissions."""

    permission_classes = [IsAuthenticated]
    serializer_class = UserInfoSerializer

    def get_object(self) -> User:
        user: User = self.request.user  # type: ignore[assignment]
        return user

    def retrieve(self, request: Request) -> Response:
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data)

    def partial_update(self, request: Request) -> Response:
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
