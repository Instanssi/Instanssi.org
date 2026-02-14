from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from Instanssi.api.v2.serializers.public.notifications import VapidPublicKeySerializer


class VapidPublicKeyView(APIView):
    """Returns the VAPID public key for push subscriptions."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: VapidPublicKeySerializer}, auth=[])
    def get(self, request: Request) -> Response:
        serializer = VapidPublicKeySerializer({"vapid_public_key": settings.VAPID_PUBLIC_KEY})
        return Response(serializer.data)
