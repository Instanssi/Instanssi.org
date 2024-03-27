from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet, ViewSet


class EnforceCSRFViewSet(ViewSet):
    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        """Enforce CSRF protection in login view."""
        return super().dispatch(request, *args, **kwargs)


class FullDjangoModelPermissions(DjangoModelPermissions):
    """Checks all permissions (by default, view perms are skipped)"""

    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": ["%(app_label)s.view_%(model_name)s"],
        "HEAD": ["%(app_label)s.view_%(model_name)s"],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }


class PermissionReadOnlyViewSet(ReadOnlyModelViewSet):
    permission_classes = [FullDjangoModelPermissions]


class PermissionViewSet(ModelViewSet):
    permission_classes = [FullDjangoModelPermissions]
