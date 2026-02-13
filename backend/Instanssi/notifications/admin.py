from django.contrib import admin

from Instanssi.notifications.models import PushSubscription, SentNotification


@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "endpoint", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "endpoint")
    raw_id_fields = ("user",)


@admin.register(SentNotification)
class SentNotificationAdmin(admin.ModelAdmin):
    list_display = ("notification_key", "sent_at")
    list_filter = ("sent_at",)
    search_fields = ("notification_key",)
