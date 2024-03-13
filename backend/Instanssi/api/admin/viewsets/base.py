from rest_framework.permissions import IsAdminUser, IsAuthenticated, DjangoModelPermissions
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet


class AdminReadOnlyViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser, DjangoModelPermissions]


class AdminViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser, DjangoModelPermissions]
