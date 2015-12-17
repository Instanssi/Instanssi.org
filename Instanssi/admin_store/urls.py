# -*- coding: utf-8 -*-

from django.conf.urls import url
from Instanssi.admin_store.views import index, items, export, status, tis, tis_csv, transaction_status,\
    edit_item, delete_item

urlpatterns = [
    url(r'^$', index, name="index"),
    url(r'^items/$', items, name="items"),
    url(r'^export/$', export, name="export"),
    url(r'^status/$', status, name="status"),
    url(r'^tis/$', tis, name="transactionitems"),
    url(r'^tis_csv/(?P<event_id>\d+)/$', tis_csv, name="transactions_csv"),
    url(r'^transactionstatus/(?P<transaction_id>\d+)/$', transaction_status, name="transactionstatus"),
    url(r'^edititem/(?P<item_id>\d+)/$', edit_item, name="edit_item"),
    url(r'^deleteitem/(?P<item_id>\d+)/$', delete_item, name="delete_item"),
]
