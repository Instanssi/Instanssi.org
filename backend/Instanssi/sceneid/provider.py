from typing import Any

from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider

from Instanssi.sceneid.views import SceneIDOAuth2Adapter


class SceneIDAccount(ProviderAccount):  # type: ignore[misc]
    def to_str(self) -> str:
        display_name = self.account.extra_data.get("display_name")
        if isinstance(display_name, str) and display_name:
            return display_name
        return str(super().to_str())


class SceneIDProvider(OAuth2Provider):  # type: ignore[misc]
    id = "sceneid"
    name = "SceneID"
    account_class = SceneIDAccount
    oauth2_adapter_class = SceneIDOAuth2Adapter

    def extract_uid(self, data: dict[str, Any]) -> str:
        return str(data["id"])

    def extract_common_fields(self, data: dict[str, Any]) -> dict[str, Any]:
        return dict(
            email=data.get("email"),
            username=data.get("display_name"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
        )

    def extract_email_addresses(self, data: dict[str, Any]) -> list[EmailAddress]:
        email = data.get("email")
        if not email:
            return []
        # SceneID verifies email addresses on registration
        return [EmailAddress(email=email, verified=True, primary=True)]

    def get_default_scope(self) -> list[str]:
        return ["basic", "user:email"]


provider_classes = [SceneIDProvider]
