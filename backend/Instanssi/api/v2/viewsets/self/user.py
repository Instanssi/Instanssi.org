from django.contrib.auth.models import User
from django.db.models import QuerySet
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from Instanssi.api.v2.serializers.user import UserDataSerializer


class UserDataViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserDataSerializer

    def get_queryset(self) -> QuerySet:
        return User.objects.filter(pk=self.request.user.pk)
