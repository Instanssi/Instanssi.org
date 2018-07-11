# -*- coding: utf-8 -*-

from django.conf.urls import url
from Instanssi.main2014.views import pageloader, reportointi, jahti, kiitos

app_name = "main2014"


urlpatterns = [
    url(r'^$', pageloader, {'templatename': 'index'}, name="index"),
    url(r'^info/$', pageloader, {'templatename': 'info'}, name="info"),
    url(r'^english/$', pageloader, {'templatename': 'english'}, name="english"),
    url(r'^yhteystiedot/$', pageloader, {'templatename': 'info'}, name="yhteystiedot"), # Show Info page
    url(r'^ohjelma/$', pageloader, {'templatename': 'ohjelma'}, name="ohjelma"),
    url(r'^aikataulu/$', pageloader, {'templatename': 'aikataulu'}, name="aikataulu"),
    url(r'^kompot/$', pageloader, {'templatename': 'kompot'}, name="kompot"),
    url(r'^kilpailusopimus/$', pageloader, {'templatename': 'kilpailusopimus'}, name="kilpailusopimus"),
    url(r'^stream/$', pageloader, {'templatename': 'stream'}, name="stream"),
    
    url(r'^toimisto/$', pageloader, {'templatename': 'toimisto/index'}, name="toimisto-index"),
    url(r'^toimisto/raportointi/$', reportointi, name="toimisto-reportointi"),
    url(r'^toimisto/qr/(?P<hint_id>\w+)/$', jahti, name="toimisto-jahti"),
    url(r'^toimisto/kiitos/$', kiitos, name="toimisto-kiitos"),
]
