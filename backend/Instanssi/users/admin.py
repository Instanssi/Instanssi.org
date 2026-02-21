from typing import Any

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from Instanssi.users.models import User


class UserAdmin(BaseUserAdmin):  # type: ignore[type-arg]
    readonly_fields = (*BaseUserAdmin.readonly_fields, "is_system", "username")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("username", "first_name", "last_name")}),
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
        (
            _("Notifications"),
            {
                "fields": (
                    "notify_vote_code_requests",
                    "notify_program_events",
                    "notify_compo_starts",
                    "notify_competition_starts",
                ),
            },
        ),
    )
    list_display = ("email", "first_name", "last_name", "is_staff")
    ordering = ("email",)

    def has_change_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        if isinstance(obj, User) and obj.is_system:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        if isinstance(obj, User) and obj.is_system:
            return False
        return super().has_delete_permission(request, obj)


admin.site.register(User, UserAdmin)
