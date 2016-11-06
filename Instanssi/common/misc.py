# -*- coding: utf-8 -*-

from django.conf import settings
from urllib.parse import urlsplit, urlunsplit, urlparse, parse_qs


def get_url(path):
    proto = 'https://' if settings.SSL_ON else 'http://'
    host = settings.DOMAIN
    return u'{}{}{}'.format(proto, host, path or '')


def get_url_local_path(url):
    parsed = urlsplit(url)
    newlist = ('', '', parsed[2], parsed[3], parsed[4])
    new = urlunsplit(newlist)
    return new


def parse_youtube_video_id(value):
    query = urlparse(value)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse_qs(query.query)
            if not p.get('v'):
                return None
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    return None
