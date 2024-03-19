from django.contrib import auth
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from Instanssi.api.v2.utils.base import EnforceCSRFViewSet


class LogoutViewSet(EnforceCSRFViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request: Request) -> Response:
        auth.logout(request)
        return Response({}, status=status.HTTP_200_OK)
