from django.contrib.auth.models import User
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema
from knox.crypto import create_token_string, hash_token
from knox.models import AuthToken
from knox.settings import CONSTANTS
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.mixins import DestroyModelMixin, ListModelMixin
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from Instanssi.api.v2.serializers.user.token_serializer import (
    AuthTokenCreateResponseSerializer,
    AuthTokenCreateSerializer,
    AuthTokenSerializer,
)
from Instanssi.api.v2.utils.base import FullDjangoModelPermissions


class UserTokenViewSet(DestroyModelMixin, ListModelMixin, GenericViewSet[AuthToken]):
    """Manage API authentication tokens for the current user.

    Requires knox.view_authtoken permission to list tokens.
    Requires knox.delete_authtoken permission to delete tokens.
    Requires knox.add_authtoken permission to create tokens.

    Users can only see and delete their own tokens.
    """

    permission_classes = [FullDjangoModelPermissions]
    serializer_class = AuthTokenSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter,)
    ordering_fields = ("created", "expiry")
    ordering = ("-created",)
    queryset = AuthToken.objects.all()

    def get_queryset(self) -> QuerySet[AuthToken]:
        """Return only the current user's tokens."""
        user: User = self.request.user  # type: ignore[assignment]
        qs: QuerySet[AuthToken] = self.queryset.filter(user=user)
        return qs

    @extend_schema(
        operation_id="user_tokens_create_token",
        request=AuthTokenCreateSerializer,
        responses={201: AuthTokenCreateResponseSerializer},
    )
    @action(detail=False, methods=["post"], url_path="create")
    def create_token(self, request: Request) -> Response:
        """Create a new API token. The plain token is returned only once."""
        serializer = AuthTokenCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Generate token string
        token_string = create_token_string()

        # Create the token object
        token = AuthToken()
        token.user = request.user
        token.digest = hash_token(token_string)
        token.token_key = token_string[: CONSTANTS.TOKEN_KEY_LENGTH]
        token.expiry = serializer.validated_data["expiry"]
        token.save()

        # Return the full token (only shown once)
        response_data = {
            "pk": str(token.pk),
            "token_key": token.token_key,
            "token": token_string,
            "created": token.created,
            "expiry": token.expiry,
        }
        return Response(
            AuthTokenCreateResponseSerializer(response_data).data,
            status=status.HTTP_201_CREATED,
        )
