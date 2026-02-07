from typing import Any

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.http import HttpRequest

from Instanssi.users.models import User


class UserAdmin(BaseUserAdmin):
    readonly_fields = (*BaseUserAdmin.readonly_fields, "is_system")

    def has_change_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        if isinstance(obj, User) and obj.is_system:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        if isinstance(obj, User) and obj.is_system:
            return False
        return super().has_delete_permission(request, obj)


admin.site.register(User, UserAdmin)
