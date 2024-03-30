from typing import Any

from django.db import IntegrityError, InterfaceError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc: Exception, context: Any) -> Response:
    if isinstance(exc, InterfaceError):
        return Response({"detail": "Database connection error"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    if isinstance(exc, IntegrityError):
        return Response({"detail": "Data integrity error"}, status=status.HTTP_409_CONFLICT)
    return exception_handler(exc, context)
