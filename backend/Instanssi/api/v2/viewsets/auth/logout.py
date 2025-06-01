from django.contrib import auth
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from Instanssi.api.v2.utils.base import EnforceCSRFViewSet


class LogoutViewSet(EnforceCSRFViewSet):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="logout",
        parameters=[],
        responses={
            200: None,
        },
    )
    def create(self, request: Request) -> Response:
        auth.logout(request)
        return Response({}, status=status.HTTP_200_OK)
