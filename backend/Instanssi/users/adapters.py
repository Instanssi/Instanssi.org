from typing import Any

from allauth.account.adapter import DefaultAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.http import HttpRequest, HttpResponseForbidden


class CustomAccountAdapter(DefaultAccountAdapter):  # type: ignore[misc]
    def pre_login(self, request: HttpRequest, user: Any, **kwargs: Any) -> Any:
        if getattr(user, "is_system", False):
            raise ImmediateHttpResponse(HttpResponseForbidden("System users cannot log in."))
        return super().pre_login(request, user, **kwargs)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):  # type: ignore[misc]
    def pre_social_login(self, request: HttpRequest, sociallogin: Any) -> None:
        user = sociallogin.user
        if getattr(user, "is_system", False):
            raise ImmediateHttpResponse(HttpResponseForbidden("System users cannot log in."))
        super().pre_social_login(request, sociallogin)
