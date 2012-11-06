# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.main2012.views',
    url(r'^$', 'pageloader', {'templatename': 'index'}),
    url(r'^info/', 'pageloader', {'templatename': 'info'}),
    url(r'^aikataulu/', 'pageloader', {'templatename': 'aikataulu'}),
    url(r'^english/', 'pageloader', {'templatename': 'english'}),
    url(r'^kompot/', 'pageloader', {'templatename': 'kompot'}),
    url(r'^ohjelma/', 'pageloader', {'templatename': 'ohjelma'}),
    url(r'^liput/', 'pageloader', {'templatename': 'liput'}),
    url(r'^stream/', 'pageloader', {'templatename': 'stream'}),
    url(r'^yhteystiedot/', 'pageloader', {'templatename': 'yhteystiedot'}),
)
