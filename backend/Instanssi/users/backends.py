from allauth.account.auth_backends import AuthenticationBackend
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.base_user import AbstractBaseUser


def _check_system_user(user: AbstractBaseUser) -> bool:
    """Reject system users from authentication."""
    return not getattr(user, "is_system", False)


class SystemUserAwareModelBackend(ModelBackend):
    def user_can_authenticate(self, user: AbstractBaseUser) -> bool:  # type: ignore[override]
        if not _check_system_user(user):
            return False
        return super().user_can_authenticate(user)  # type: ignore[arg-type]


class SystemUserAwareAllAuthBackend(AuthenticationBackend):  # type: ignore[misc]
    def user_can_authenticate(self, user: AbstractBaseUser) -> bool:
        if not _check_system_user(user):
            return False
        return bool(super().user_can_authenticate(user))
