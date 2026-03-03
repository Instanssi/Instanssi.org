from typing import Any

from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailAddress
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

    def can_delete_email(self, email_address: EmailAddress) -> bool:
        # Ensure users always retain at least one verified email.
        # Without this, allauth's default allows removing all emails when
        # username login is enabled, which would block API login when
        # ACCOUNT_EMAIL_VERIFICATION is "mandatory".
        if not email_address.verified:
            return True
        has_other_verified = (
            EmailAddress.objects.filter(user_id=email_address.user_id, verified=True)
            .exclude(pk=email_address.pk)
            .exists()
        )
        return has_other_verified  # type: ignore[no-any-return]


class InstanssiSocialAccountAdapter(DefaultSocialAccountAdapter):  # type: ignore[misc]
    def is_auto_signup_allowed(self, request: HttpRequest, sociallogin: Any) -> bool:
        if sociallogin.account.provider in _NO_AUTO_SIGNUP_PROVIDERS:
            return False
        return super().is_auto_signup_allowed(request, sociallogin)  # type: ignore[no-any-return]
