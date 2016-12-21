# -*- coding: utf-8 -*-

from django.contrib import admin
from Instanssi.store.models import StoreItem, StoreTransaction, TransactionItem, StoreItemVariant


admin.site.register(StoreItem)
admin.site.register(StoreTransaction)
admin.site.register(TransactionItem)
admin.site.register(StoreItemVariant)
