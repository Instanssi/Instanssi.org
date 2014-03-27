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
    url(r'^order_search_ac', 'order_search_ac', name="order_search_ac"),
    url(r'^order_search', 'order_search', name="order_search"),
)
