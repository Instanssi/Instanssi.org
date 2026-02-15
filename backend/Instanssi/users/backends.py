from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.base_user import AbstractBaseUser


class SystemUserAwareModelBackend(ModelBackend):
    def user_can_authenticate(self, user: AbstractBaseUser) -> bool:  # type: ignore[override]
        if getattr(user, "is_system", False):
            return False
        return super().user_can_authenticate(user)  # type: ignore[arg-type]
