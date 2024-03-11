import logging

import yarl
from django.contrib import auth
from django.urls import reverse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ViewSet

from Instanssi.api.auth.serializers import UserDataSerializer, UserLoginSerializer
from Instanssi.api.utils import IsAuthenticatedOrWriteOnly
from Instanssi.users.views import AUTH_METHODS

logger = logging.getLogger(__name__)


class UserDataViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserDataSerializer

    def get_object(self):
        return self.request.user

    def list(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class LogoutViewSet(ViewSet):
    permission_classes = [IsAuthenticatedOrWriteOnly]
    authentication_classes = []

    def create(self, request: Request) -> Response:
        auth.logout(request)
        return Response({}, status=status.HTTP_200_OK)


class LoginViewSet(ViewSet):
    permission_classes = [IsAuthenticatedOrWriteOnly]
    authentication_classes = []

    def create(self, request: Request) -> Response:
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]
            user = auth.authenticate(username=username, password=password)
            if user and user.is_active:
                auth.login(request, user)
                return Response({}, status=status.HTTP_200_OK)
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BeginSocialAuthViewSet(ViewSet):
    """
    Returns a list of URLs that can be used to begin a social authentication process.
    """

    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = []

    def list(self, request: Request, *args, **kwargs):
        methods = []
        default_next = reverse("users:login")
        found_next = request.query_params.get("next", default_next)
        for method in AUTH_METHODS:
            url = yarl.URL(
                reverse(
                    viewname="social:begin",
                    args=(method[0],),
                )
            ).update_query(next=found_next)
            methods.append(
                dict(
                    method=method[0],
                    url=str(url),
                    name=method[2],
                )
            )
        return Response(methods, status=status.HTTP_200_OK)
