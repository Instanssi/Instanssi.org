from typing import Any

from rest_framework.permissions import (
    DjangoModelPermissions,
    IsAdminUser,
    IsAuthenticated,
)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet


class AdminReadOnlyViewSet(ReadOnlyModelViewSet[Any]):
    permission_classes = [IsAuthenticated, IsAdminUser, DjangoModelPermissions]


class AdminViewSet(ModelViewSet[Any]):
    permission_classes = [IsAuthenticated, IsAdminUser, DjangoModelPermissions]
