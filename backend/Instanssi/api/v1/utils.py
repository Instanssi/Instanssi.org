from typing import Any

from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import GenericViewSet


class WriteOnlyModelViewSet(CreateModelMixin, GenericViewSet[Any]):
    pass
