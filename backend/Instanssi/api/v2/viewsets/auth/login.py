from allauth.account import app_settings as account_settings
from allauth.account.utils import has_verified_email
from django.contrib import auth
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from Instanssi.api.v2.serializers.auth import UserLoginSerializer
from Instanssi.api.v2.utils.base import EnforceCSRFViewSet


class LoginViewSet(EnforceCSRFViewSet):
    """Authenticate a user with username and password."""

    @extend_schema(
        operation_id="login",
        request=UserLoginSerializer,
        responses={
            200: None,
            400: None,
            401: None,
            403: None,
        },
    )
    def create(self, request: Request) -> Response:
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]
            user = auth.authenticate(username=username, password=password)
            if user and user.is_active:
                if (
                    account_settings.EMAIL_VERIFICATION == account_settings.EmailVerificationMethod.MANDATORY
                    and not has_verified_email(user)
                ):
                    return Response({"code": "email_not_verified"}, status=status.HTTP_403_FORBIDDEN)
                auth.login(request, user)
                return Response({}, status=status.HTTP_200_OK)
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
