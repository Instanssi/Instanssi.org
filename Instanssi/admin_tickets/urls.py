# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_tickets.views',
    url(r'^$', 'index', name="index"),
    url(r'^edit/(?P<ticket_id>\d+)/', 'edit_ticket', name="edit"),
)