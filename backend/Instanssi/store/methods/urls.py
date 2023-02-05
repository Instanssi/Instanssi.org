from django.urls import path

from Instanssi.store.methods import no_method, paytrail

app_name = "store"


urlpatterns = [
    # Test only
    path("nomethod/success/", no_method.handle_success, name="no-method-success"),
    # Paytrail
    path("paytrail/success/", paytrail.handle_success, name="paytrail-success"),
    path("paytrail/cancel/", paytrail.handle_cancel, name="paytrail-cancel"),
    path("paytrail/redirect/success/", paytrail.handle_redirect_success, name="paytrail-redirect-success"),
    path("paytrail/redirect/cancel/", paytrail.handle_redirect_cancel, name="paytrail-redirect-cancel"),
    path("paytrail/callback/", paytrail.handle_callback, name="paytrail-callback"),
]
