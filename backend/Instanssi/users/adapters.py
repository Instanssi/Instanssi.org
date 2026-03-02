from typing import Any

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.http import HttpRequest
from django.urls import reverse

# Providers that don't provide an email address at all.
# Users logging in via these providers will always see the signup form
# so they can provide an email.
_NO_AUTO_SIGNUP_PROVIDERS = frozenset({"steam"})


class InstanssiAccountAdapter(DefaultAccountAdapter):  # type: ignore[misc]
    def get_login_redirect_url(self, request: HttpRequest) -> str:
        return reverse("users:profile")

    def get_logout_redirect_url(self, request: HttpRequest) -> str:
        return reverse("users:loggedout")


class InstanssiSocialAccountAdapter(DefaultSocialAccountAdapter):  # type: ignore[misc]
    def is_auto_signup_allowed(self, request: HttpRequest, sociallogin: Any) -> bool:
        if sociallogin.account.provider in _NO_AUTO_SIGNUP_PROVIDERS:
            return False
        return super().is_auto_signup_allowed(request, sociallogin)  # type: ignore[no-any-return]
