from django.urls import path

from Instanssi.infodesk.views import (
    index,
    item_check,
    item_info,
    item_mark,
    order_search,
    order_search_ac,
    transaction_check,
    transaction_info,
)

app_name = "infodesk"


urlpatterns = [
    path("", index, name="index"),
    path("item/check/", item_check, name="item_check"),
    path("transaction/check/", transaction_check, name="transaction_check"),
    path("item/info/<int:item_id>/", item_info, name="item_info"),
    path("transaction/info/<int:transaction_id>/", transaction_info, name="transaction_info"),
    path("item/mark/<int:item_id>/", item_mark, name="item_mark"),
    path("order_search_ac", order_search_ac, name="order_search_ac"),
    path("order_search", order_search, name="order_search"),
]
