# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'Instanssi.infodesk.views',
    url(r'^$', 'index', name="index"),
    url(r'^item/check/', 'item_check', name="item_check"),
    url(r'^transaction/check/', 'transaction_check', name="transaction_check"),
    url(r'^item/info/(?P<item_id>\d+)/', 'item_info', name="item_info"),
    url(r'^transaction/info/(?P<transaction_id>\d+)/', 'transaction_info', name="transaction_info"),
    url(r'^item/mark/(?P<item_id>\d+)/', 'item_mark', name="item_mark"),
    url(r'^ta_lookup_ac', 'ta_lookup_autocomplete', name="ta_lookup_autocomplete"),
    url(r'^ta_lookup', 'ta_lookup', name="ta_lookup"),
)
