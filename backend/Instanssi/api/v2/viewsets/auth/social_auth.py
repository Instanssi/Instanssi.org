from typing import Any

import yarl
from django.http import HttpRequest, HttpResponseBase
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from Instanssi.api.v2.serializers.auth import SocialAuthURLSerializer
from Instanssi.users.views import AUTH_METHODS


class SocialAuthUrlsViewSet(ViewSet):
    """
    Returns a list of URLs that can be used to begin a social authentication process.

    Also ensures the CSRF cookie is set, which is needed for the SPA login flow.
    Without this, the first login attempt in a fresh browser session would fail
    because no Django template renders {% csrf_token %} to trigger cookie creation.
    """

    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = []

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
        return super().dispatch(request, *args, **kwargs)

    @extend_schema(
        operation_id="get_social_auth_urls",
        parameters=[
            OpenApiParameter("next"),
        ],
        responses={200: SocialAuthURLSerializer},
    )
    def list(self, request: Request) -> Response:
        methods = []
        default_next = reverse("users:login")
        found_next = request.query_params.get("next", default_next)
        for method in AUTH_METHODS:
            url = yarl.URL(
                reverse(
                    viewname="social:begin",
                    args=(method[1],),
                )
            ).update_query(next=found_next)
            methods.append(
                dict(
                    method=method[0],
                    url=str(url),
                    name=method[2],
                )
            )
        data = SocialAuthURLSerializer(instance=methods, many=True).data  # type: ignore[arg-type]
        return Response(data, status=status.HTTP_200_OK)
