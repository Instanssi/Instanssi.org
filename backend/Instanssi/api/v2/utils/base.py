from typing import Any, TypeVar

from django.db.models import Model
from django.http import HttpRequest, HttpResponseBase
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework.mixins import CreateModelMixin
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, DjangoModelPermissions
from rest_framework.viewsets import (
    GenericViewSet,
    ModelViewSet,
    ReadOnlyModelViewSet,
    ViewSet,
)

_ModelT = TypeVar("_ModelT", bound=Model)


class EnforceCSRFViewSet(ViewSet):
    """ViewSet base class that enforces CSRF protection.

    Used for authentication endpoints (login) where CSRF protection is critical.
    Applies three security decorators:
    - sensitive_post_parameters: Prevents password logging in error reports
    - csrf_protect: Requires valid CSRF token
    - never_cache: Prevents caching of responses
    """

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
        return super().dispatch(request, *args, **kwargs)


class FullDjangoModelPermissions(DjangoModelPermissions):
    """Permission class that checks Django model permissions for all HTTP methods.

    Unlike the default DjangoModelPermissions, this also requires view permissions
    for GET/HEAD/OPTIONS requests. This ensures staff users must have explicit
    permissions to access any endpoint.

    Permission mapping:
        GET, HEAD, OPTIONS -> {app}.view_{model}
        POST               -> {app}.add_{model}
        PUT, PATCH         -> {app}.change_{model}
        DELETE             -> {app}.delete_{model}

    Example:
        For a StoreItem model in the 'store' app:
        - GET requires 'store.view_storeitem'
        - POST requires 'store.add_storeitem'
        - PUT/PATCH requires 'store.change_storeitem'
        - DELETE requires 'store.delete_storeitem'
    """

    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": ["%(app_label)s.view_%(model_name)s"],
        "HEAD": ["%(app_label)s.view_%(model_name)s"],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }


class PermissionReadOnlyViewSet(ReadOnlyModelViewSet[Model]):
    """Read-only viewset that requires Django model view permissions.

    Provides list and retrieve actions only. Users must have the
    {app}.view_{model} permission to access any endpoint.

    Use for data that should only be readable by staff with explicit permissions.
    """

    permission_classes = [FullDjangoModelPermissions]


class PermissionViewSet(ModelViewSet[Model]):
    """Full CRUD viewset that requires Django model permissions.

    Provides list, retrieve, create, update, partial_update, and destroy actions.
    Each action requires the corresponding Django model permission.

    This is the standard base class for staff-only API endpoints.
    """

    permission_classes = [FullDjangoModelPermissions]


class PublicReadOnlyViewSet(ReadOnlyModelViewSet[_ModelT]):
    """Read-only viewset for public endpoints requiring no authentication.

    Sets AllowAny permissions, disables authentication, and uses
    LimitOffsetPagination. All public read-only viewsets should inherit
    from this instead of ReadOnlyModelViewSet.
    """

    permission_classes = [AllowAny]
    authentication_classes: list[type] = []
    pagination_class = LimitOffsetPagination


class WriteOnlyModelViewSet(CreateModelMixin, GenericViewSet[Model]):
    """Write-only viewset that only supports create operations.

    Provides only the create action (POST). Useful for endpoints like
    public checkout where users submit data but don't need to list or
    retrieve existing records.
    """

    pass
