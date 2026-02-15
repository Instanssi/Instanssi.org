import logging
from typing import Any

from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from Instanssi.api.v1.serializers.user import UserSerializer
from Instanssi.users.models import User

logger = logging.getLogger(__name__)


class CurrentUserViewSet(ReadOnlyModelViewSet[User]):
    """
    Shows data to the authenticated user about self
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self) -> User:
        return self.request.user  # type: ignore[return-value]

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return self.retrieve(request, *args, **kwargs)
