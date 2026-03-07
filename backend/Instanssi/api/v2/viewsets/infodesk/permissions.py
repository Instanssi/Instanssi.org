from rest_framework.permissions import BasePermission


class HasInfodeskViewPermission(BasePermission):
    def has_permission(self, request, view) -> bool:  # type: ignore[no-untyped-def]
        return bool(request.user.has_perm("infodesk.view_infodeskaccess"))


class HasInfodeskChangePermission(BasePermission):
    def has_permission(self, request, view) -> bool:  # type: ignore[no-untyped-def]
        return bool(request.user.has_perm("infodesk.change_infodeskaccess"))
