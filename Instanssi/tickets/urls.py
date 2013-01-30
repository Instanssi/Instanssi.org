# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.tickets.views',
    url(r'^info/(?P<ticket_key>\w+)/', 'ticket', name="ticket"),
    url(r'^ta/(?P<transaction_key>\w+)/', 'tickets', name="tickets"),
)
