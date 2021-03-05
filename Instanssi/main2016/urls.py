# -*- coding: utf-8 -*-

from django.conf.urls import url
from Instanssi.main2016.views import pageloader

app_name = "main2016"


urlpatterns = [
    url(r'^$', pageloader, {'templatename': 'index'}, name="index"),
    url(r'^info/$', pageloader, {'templatename': 'info'}, name="info"),
    url(r'^english/$', pageloader, {'templatename': 'english'}, name="english"),
    url(r'^yhteystiedot/$', pageloader, {'templatename': 'info'}, name="yhteystiedot"),
    url(r'^ohjelma/$', pageloader, {'templatename': 'ohjelma'}, name="ohjelma"),
    url(r'^aikataulu/$', pageloader, {'templatename': 'aikataulu'}, name="aikataulu"),
    url(r'^kompot/$', pageloader, {'templatename': 'kompot'}, name="kompot"),
    url(r'^kilpailusopimus/$', pageloader, {'templatename': 'kilpailusopimus'}, name="kilpailusopimus"),
    url(r'^stream/$', pageloader, {'templatename': 'stream'}, name="stream"),
]
