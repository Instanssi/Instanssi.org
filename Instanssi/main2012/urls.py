# -*- coding: utf-8 -*-

from django.conf.urls import url
from Instanssi.main2012.views import pageloader

app_name = "main2012"


urlpatterns = [
    url(r'^$', pageloader, {'templatename': 'index'}, name="index"),
    url(r'^info/', pageloader, {'templatename': 'info'}, name="info"),
    url(r'^aikataulu/', pageloader, {'templatename': 'aikataulu'}, name="aikataulu"),
    url(r'^english/', pageloader, {'templatename': 'english'}, name="english"),
    url(r'^kompot/', pageloader, {'templatename': 'kompot'}, name="kompot"),
    url(r'^ohjelma/', pageloader, {'templatename': 'ohjelma'}, name="ohjelma"),
    url(r'^liput/', pageloader, {'templatename': 'liput'}, name="liput"),
    url(r'^stream/', pageloader, {'templatename': 'stream'}, name="stream"),
    url(r'^yhteystiedot/', pageloader, {'templatename': 'yhteystiedot'}, name="yhteystiedot"),
]
