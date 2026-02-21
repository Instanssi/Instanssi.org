from allauth.account.auth_backends import AuthenticationBackend
from django.contrib.auth.base_user import AbstractBaseUser


class SystemUserAwareAuthBackend(AuthenticationBackend):  # type: ignore[misc]
    def user_can_authenticate(self, user: AbstractBaseUser) -> bool:
        if getattr(user, "is_system", False):
            return False
        return super().user_can_authenticate(user)  # type: ignore[no-any-return]
