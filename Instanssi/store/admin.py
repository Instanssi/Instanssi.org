# -*- coding: utf-8 -*-

from django.contrib import admin
from Instanssi.store.models import StoreItem, StoreTransaction, TransactionItem, StoreItemVariant, Receipt


class StoreTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'firstname',
        'lastname',
        'email',
        'token',
        'time_created',
        'time_pending',
        'time_paid',
        'time_cancelled',
        'payment_method_name',
    ]


class TransactionItemAdmin(admin.ModelAdmin):
    list_display = [
        'key',
        'item',
        'variant',
        'transaction',
        'time_delivered',
    ]


class ReceiptAdmin(admin.ModelAdmin):
    list_display = [
        'mail_to',
        'mail_from',
        'subject',
        'sent',
    ]


class StoreItemAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'event',
        'price',
        'max',
        'max_per_order',
        'available',
        'discount_amount',
        'discount_percentage',
        'is_ticket',
        'is_secret',
    ]


admin.site.register(StoreItem, StoreItemAdmin)
admin.site.register(StoreTransaction, StoreTransactionAdmin)
admin.site.register(TransactionItem, TransactionItemAdmin)
admin.site.register(StoreItemVariant)
admin.site.register(Receipt, ReceiptAdmin)
