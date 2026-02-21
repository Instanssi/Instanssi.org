from typing import Any

from allauth.account.adapter import DefaultAccountAdapter


class AccountAdapter(DefaultAccountAdapter):  # type: ignore[misc]
    def pre_login(self, request: Any, user: Any, **kwargs: Any) -> Any:
        """Block system users from logging in via allauth views/headless API."""
        if getattr(user, "is_system", False):
            return self.respond_user_inactive(request, user)
        return super().pre_login(request, user, **kwargs)
