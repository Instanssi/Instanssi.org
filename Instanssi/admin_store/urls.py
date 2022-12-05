from django.urls import path

from Instanssi.admin_store.views import (
    amounts,
    delete_item,
    edit_item,
    export,
    index,
    items,
    status,
    tis,
    tis_csv,
    transaction_status,
)

app_name = "admin_store"


urlpatterns = [
    path("", index, name="index"),
    path("items/", items, name="items"),
    path("amounts/", amounts, name="amounts"),
    path("export/", export, name="export"),
    path("status/", status, name="status"),
    path("tis/", tis, name="transactionitems"),
    path("tis_csv/<int:event_id>/", tis_csv, name="transactions_csv"),
    path("transactionstatus/<int:transaction_id>/", transaction_status, name="transactionstatus"),
    path("edititem/<int:item_id>/", edit_item, name="edit_item"),
    path("deleteitem/<int:item_id>/", delete_item, name="delete_item"),
]
