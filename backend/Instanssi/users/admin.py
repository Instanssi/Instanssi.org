from typing import Any

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from Instanssi.users.models import User


class UserAdmin(BaseUserAdmin):
    readonly_fields = (*BaseUserAdmin.readonly_fields, "is_system")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_system",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    def has_change_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        if isinstance(obj, User) and obj.is_system:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        if isinstance(obj, User) and obj.is_system:
            return False
        return super().has_delete_permission(request, obj)


admin.site.register(User, UserAdmin)
