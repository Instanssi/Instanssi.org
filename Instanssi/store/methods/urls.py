from django.urls import path

from Instanssi.store.methods import no_method, paytrail

app_name = "store"


urlpatterns = [
    path("nomethod/success/", no_method.handle_success, name="no-method-success"),
    path("paytrail/notify/", paytrail.handle_notify, name="paytrail-notify"),
    path("paytrail/failure/", paytrail.handle_failure, name="paytrail-failure"),
    path("paytrail/success/", paytrail.handle_success, name="paytrail-success"),
]
