# -*- coding: utf-8 -*-

from django.conf import settings
from urlparse import urlsplit, urlunsplit


def get_url(path):
    proto = 'https://' if settings.SSL_ON else 'http://'
    host = settings.DOMAIN
    return u'{}{}{}'.format(proto, host, path or '')


def get_url_local_path(url):
    parsed = urlsplit(url)
    newlist = ('', '', parsed[2], parsed[3], parsed[4])
    new = urlunsplit(newlist)
    return new
