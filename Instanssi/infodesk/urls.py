# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns(
    'Instanssi.infodesk.views',
    url(r'^(?P<event_id>\d+)/$', 'index', name="index"),
    url(r'^(?P<event_id>\d+)/ticket/check/', 'ticket_check', name="ticket_check"),
    url(r'^(?P<event_id>\d+)/store/check/', 'store_check', name="store_check"),
    url(r'^(?P<event_id>\d+)/ticket/info/(?P<ticket_id>\d+)/', 'ticket_info', name="ticket_info"),
    url(r'^(?P<event_id>\d+)/store/info/(?P<transaction_id>\d+)/', 'store_info', name="store_info"),
    url(r'^(?P<event_id>\d+)/ticket/mark/(?P<ticket_id>\d+)/', 'ticket_mark', name="mark_ticket"),
    url(r'^(?P<event_id>\d+)/store/mark/(?P<transaction_id>\d+)/', 'store_mark', name="mark_transaction"),
)
