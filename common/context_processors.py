# -*- coding: utf-8 -*-

from django.conf import settings
from django_openid_auth.models import UserOpenID

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
    
def openid_helper(request):
    if not request.user.is_authenticated():
        return {'is_openiduser': False}
    
    try:
        r = UserOpenID.objects.get(user=request.user)
        return {'is_openiduser': True}
    except UserOpenID.DoesNotExist:
        pass
    return {'is_openiduser': False}
    