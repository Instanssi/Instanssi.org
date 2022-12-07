from typing import Dict

from django.conf import settings
from django.http import HttpRequest


def short_language_code(_: HttpRequest) -> Dict:
    return {
        "SHORT_LANGUAGE_CODE": settings.SHORT_LANGUAGE_CODE,
    }


def google_settings(_: HttpRequest) -> Dict:
    return {
        "GOOGLE_API_KEY": settings.GOOGLE_API_KEY,
        "GOOGLE_ANALYTICS": settings.GOOGLE_ANALYTICS,
        "GOOGLE_ANALYTICS_CODE": settings.GOOGLE_ANALYTICS_CODE,
    }
