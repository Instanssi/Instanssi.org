from typing import Any

from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.models import SocialLogin, SocialToken
from allauth.socialaccount.providers.base import ProviderException
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)
from django.http import HttpRequest


class SceneIDOAuth2Adapter(OAuth2Adapter):  # type: ignore[misc]
    provider_id = "sceneid"
    access_token_url = "https://id.scene.org/oauth/token/"
    authorize_url = "https://id.scene.org/oauth/authorize/"
    profile_url = "https://id.scene.org/api/3.0/me/"

    # SceneID requires client credentials via HTTP basic auth on the token endpoint
    basic_auth = True

    def complete_login(
        self, request: HttpRequest, app: Any, token: SocialToken, **kwargs: Any
    ) -> SocialLogin:
        headers = {"Authorization": f"Bearer {token.token}"}
        with get_adapter().get_requests_session() as sess:
            resp = sess.get(self.profile_url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        if not data.get("success") or "user" not in data:
            raise ProviderException("SceneID profile request was unsuccessful")
        return self.get_provider().sociallogin_from_response(request, data["user"])


oauth2_login = OAuth2LoginView.adapter_view(SceneIDOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(SceneIDOAuth2Adapter)
