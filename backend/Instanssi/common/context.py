from typing import Any

from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest


class Settings:
    def __init__(self, values: dict[str, Any]) -> None:
        self.values: dict[str, Any] = values

    def __getitem__(self, key: str) -> Any:
        try:
            return self.values[key]
        except KeyError:
            raise ImproperlyConfigured(f"The '{key}' setting key has not been exported")


def settings_export(_: HttpRequest) -> dict[str, Any]:
    exported: dict[str, Any] = {}
    for key in getattr(django_settings, "TEMPLATE_SETTINGS_EXPORT", []):
        exported[key] = getattr(django_settings, key)
    return {"settings": Settings(exported)}
