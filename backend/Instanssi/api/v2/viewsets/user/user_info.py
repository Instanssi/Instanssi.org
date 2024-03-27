from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from Instanssi.api.v2.serializers.user import UserInfoSerializer


class UserInfoViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="user_info",
        request=None,
        responses={
            200: UserInfoSerializer,
        },
    )
    def list(self, request: Request) -> Response:
        obj = User.objects.filter(pk=request.user.pk)
        data = UserInfoSerializer(obj, many=True).data
        return Response(data, status=status.HTTP_200_OK)
