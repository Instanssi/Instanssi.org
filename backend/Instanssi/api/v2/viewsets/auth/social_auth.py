import yarl
from django.urls import reverse
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from Instanssi.users.views import AUTH_METHODS


class BeginSocialAuthViewSet(ViewSet):
    """
    Returns a list of URLs that can be used to begin a social authentication process.
    """

    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = []

    def list(self, request: Request) -> Response:
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
