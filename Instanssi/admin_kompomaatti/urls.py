# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_kompomaatti.views',
    url(r'^$', 'compos'),
    url(r'^compos/', 'compos'),
    url(r'^entries/', 'entries'),
    url(r'^results/', 'results'),
    url(r'^votecodes/', 'votecodes'),
    url(r'^votecoderequests/', 'votecoderequests'),
)