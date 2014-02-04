# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'Instanssi.main2014.views',
    url(r'^$', 'pageloader', {'templatename': 'index'}, name="index"),
	url(r'^info/', 'pageloader', {'templatename': 'info'}, name="info"),
    url(r'^english/', 'pageloader', {'templatename': 'english'}, name="english"),
    url(r'^yhteystiedot/', 'pageloader', {'templatename': 'yhteystiedot'}, name="yhteystiedot"),
    url(r'^kompot/', 'pageloader', {'templatename': 'kompot'}, name="kompot"),
    url(r'^kilpailusopimus/', 'pageloader', {'templatename': 'kilpailusopimus'}, name="kilpailusopimus"),
)
