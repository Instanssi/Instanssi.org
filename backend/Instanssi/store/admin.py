from typing import TYPE_CHECKING

from csvexport.actions import csvexport  # type: ignore[import-untyped]
from django.contrib import admin

from Instanssi.store.models import (
    Receipt,
    StoreItem,
    StoreItemVariant,
    StoreTransaction,
    StoreTransactionEvent,
    TransactionItem,
)

if TYPE_CHECKING:
    _StoreTransactionAdminBase = admin.ModelAdmin[StoreTransaction]
    _StoreTransactionEventAdminBase = admin.ModelAdmin[StoreTransactionEvent]
    _TransactionItemAdminBase = admin.ModelAdmin[TransactionItem]
    _ReceiptAdminBase = admin.ModelAdmin[Receipt]
    _StoreItemAdminBase = admin.ModelAdmin[StoreItem]
else:
    _StoreTransactionAdminBase = admin.ModelAdmin
    _StoreTransactionEventAdminBase = admin.ModelAdmin
    _TransactionItemAdminBase = admin.ModelAdmin
    _ReceiptAdminBase = admin.ModelAdmin
    _StoreItemAdminBase = admin.ModelAdmin


class StoreTransactionAdmin(_StoreTransactionAdminBase):
    actions = [csvexport]
    list_per_page = 200
    list_display = [
        "firstname",
        "lastname",
        "email",
        "token",
        "time_created",
        "time_pending",
        "time_paid",
        "time_cancelled",
        "payment_method_name",
    ]


class StoreTransactionEventAdmin(_StoreTransactionEventAdminBase):
    actions = [csvexport]
    list_per_page = 200
    list_display = [
        "transaction",
        "message",
        "data",
        "created",
    ]


class TransactionItemAdmin(_TransactionItemAdminBase):
    actions = [csvexport]
    list_per_page = 200
    list_display = [
        "key",
        "item",
        "variant",
        "transaction",
        "time_delivered",
    ]


class ReceiptAdmin(_ReceiptAdminBase):
    actions = [csvexport]
    list_per_page = 200
    list_display = [
        "transaction",
        "mail_to",
        "mail_from",
        "subject",
        "sent",
    ]


class StoreItemAdmin(_StoreItemAdminBase):
    actions = [csvexport]
    list_display = [
        "name",
        "event",
        "price",
        "max",
        "max_per_order",
        "available",
        "discount_amount",
        "discount_percentage",
        "is_ticket",
        "is_secret",
    ]


admin.site.register(StoreItem, StoreItemAdmin)
admin.site.register(StoreTransaction, StoreTransactionAdmin)
admin.site.register(StoreTransactionEvent, StoreTransactionEventAdmin)
admin.site.register(TransactionItem, TransactionItemAdmin)
admin.site.register(StoreItemVariant)
admin.site.register(Receipt, ReceiptAdmin)
