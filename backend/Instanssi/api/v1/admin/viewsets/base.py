from typing import Generic, TypeVar

from django.db.models import Model
from rest_framework.permissions import (
    DjangoModelPermissions,
    IsAdminUser,
    IsAuthenticated,
)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

_T = TypeVar("_T", bound=Model)


class AdminReadOnlyViewSet(ReadOnlyModelViewSet[_T], Generic[_T]):
    permission_classes = [IsAuthenticated, IsAdminUser, DjangoModelPermissions]


class AdminViewSet(ModelViewSet[_T], Generic[_T]):
    permission_classes = [IsAuthenticated, IsAdminUser, DjangoModelPermissions]
