# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns(
    'Instanssi.infodesk.views',
    url(r'^$', 'index', name="index"),
    url(r'^ticket/check/', 'ticket_check', name="ticket_check"),
    url(r'^store/check/', 'store_check', name="store_check"),
    url(r'^ticket/info/(?P<ticket_id>\d+)/', 'ticket_info', name="ticket_info"),
    url(r'^store/info/(?P<transaction_id>\d+)/', 'store_info', name="store_info"),
)
