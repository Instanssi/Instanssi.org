# -*- coding: utf-8 -*-

from django.conf import settings

def get_url(path):
    proto = 'https://' if settings.SSL_ON else 'http://'
    host = settings.DOMAIN
    return '%s%s%s' % (proto, host, path or '')