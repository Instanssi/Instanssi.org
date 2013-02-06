# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.main2013.views',
    url(r'^$', 'pageloader', {'templatename': 'index'}, name="index"),
	url(r'^info/', 'pageloader', {'templatename': 'info'}, name="info"),
    url(r'^aikataulu/', 'pageloader', {'templatename': 'aikataulu'}, name="aikataulu"),
    url(r'^english/', 'pageloader', {'templatename': 'english'}, name="english"),
    url(r'^kompot/', 'pageloader', {'templatename': 'kompot'}, name="kompot"),
    url(r'^ohjelma/', 'pageloader', {'templatename': 'ohjelma'}, name="ohjelma"),
    url(r'^stream/', 'pageloader', {'templatename': 'stream'}, name="stream"),
    url(r'^yhteystiedot/', 'pageloader', {'templatename': 'yhteystiedot'}, name="yhteystiedot"),
    url(r'^stream/', 'pageloader', {'templatename': 'stream'}, name="stream"),
    url(r'^liput/', 'pageloader', {'templatename': 'liput'}, name="liput"),
    
    # Store related
    url(r'^store/', 'store', name="store"),
    url(r'^store_success/', 'pageloader', {'templatename': 'store_success'}, name="store_success"),
    url(r'^store_failure/', 'store_failure', name="store_failure"),
)
