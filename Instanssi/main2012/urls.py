# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'main2012.views',
    url(r'^$', 'index'),
    url(r'^info/', 'info'),
    url(r'^aikataulu/', 'aikataulu'),
    url(r'^english/', 'english'),
    url(r'^kompot/', 'kompot'),
    url(r'^ohjelma/', 'ohjelma'),
    url(r'^liput/', 'liput'),
    url(r'^stream/', 'stream'),
    url(r'^yhteystiedot/', 'yhteystiedot'),
    url(r'^updateblog/', 'updateblog'),
)
