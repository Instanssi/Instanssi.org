from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet


class AdminReadOnlyViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]


class AdminViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
