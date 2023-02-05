from django.contrib import admin

from Instanssi.store.models import (
    Receipt,
    StoreItem,
    StoreItemVariant,
    StoreTransaction,
    StoreTransactionEvent,
    TransactionItem,
)


class StoreTransactionAdmin(admin.ModelAdmin):
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


class StoreTransactionEventAdmin(admin.ModelAdmin):
    list_display = [
        "transaction",
        "message",
        "data",
        "created",
    ]


class TransactionItemAdmin(admin.ModelAdmin):
    list_display = [
        "key",
        "item",
        "variant",
        "transaction",
        "time_delivered",
    ]


class ReceiptAdmin(admin.ModelAdmin):
    list_display = [
        "transaction",
        "mail_to",
        "mail_from",
        "subject",
        "sent",
    ]


class StoreItemAdmin(admin.ModelAdmin):
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
