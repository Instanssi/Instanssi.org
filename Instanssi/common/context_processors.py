from django.conf import settings


def short_language_code(request):
    return {
        'SHORT_LANGUAGE_CODE': settings.SHORT_LANGUAGE_CODE,
    }


def google_settings(request):
    return {
        'GOOGLE_API_KEY': settings.GOOGLE_API_KEY,
        'GOOGLE_ANALYTICS': settings.GOOGLE_ANALYTICS,
        'GOOGLE_ANALYTICS_CODE': settings.GOOGLE_ANALYTICS_CODE,
    }
