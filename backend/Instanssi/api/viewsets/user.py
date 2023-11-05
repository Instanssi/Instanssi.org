import logging

from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from Instanssi.api.serializers.user import UserSerializer

logger = logging.getLogger(__name__)


class CurrentUserViewSet(ReadOnlyModelViewSet):
    """
    Shows data to the authenticated user about self
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        pass

    def list(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
