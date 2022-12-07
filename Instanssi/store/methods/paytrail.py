import logging

from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from Instanssi.store.models import StoreTransaction
from Instanssi.store.utils import paytrail, ta_common

logger = logging.getLogger(__name__)


def start_process(request: HttpRequest, ta: StoreTransaction) -> str:
    """This should be used to start the paytrail payment process.
    Will redirect as necessary."""

    product_list = []

    for store_item, item_variant, purchase_price in ta.get_distinct_storeitems_and_prices():
        count = ta.get_storeitem_count(store_item, variant=item_variant)
        product_list.append(
            {
                "title": "{}, {}".format(store_item.name, item_variant.name)
                if item_variant
                else store_item.name,
                "code": "{}:{}".format(store_item.id, item_variant.id)
                if item_variant
                else str(store_item.id),
                "amount": str(count),
                "price": str(purchase_price),
                "vat": "0",
                "type": 1,
            }
        )

    data = {
        "orderNumber": str(ta.id),
        "currency": "EUR",
        "locale": "fi_FI",
        "urlSet": {
            "success": request.build_absolute_uri(reverse("store:pm:paytrail-success")),
            "failure": request.build_absolute_uri(reverse("store:pm:paytrail-failure")),
            "notification": request.build_absolute_uri(reverse("store:pm:paytrail-notify")),
            "pending": "",
        },
        "orderDetails": {
            "includeVat": 1,
            "contact": {
                "telephone": ta.telephone,
                "mobile": ta.mobile,
                "email": ta.email,
                "firstName": ta.firstname,
                "lastName": ta.lastname,
                "companyName": ta.company,
                "address": {
                    "street": ta.street,
                    "postalCode": ta.postalcode,
                    "postalOffice": ta.city,
                    "country": ta.country.code,
                },
            },
            "products": product_list,
        },
    }

    # Make a request
    try:
        msg = paytrail.request(
            settings.PAYTRAIL_API_URL, settings.PAYTRAIL_ID, settings.PAYTRAIL_SECRET, data
        )
    except paytrail.PaytrailException as ex:
        a, b = ex.args
        logger.exception("(%s) %s", b, a)
        return reverse("store:pm:paytrail-failure")
    except Exception as ex:
        logger.exception("%s.", ex)
        return reverse("store:pm:paytrail-failure")

    # Save token, redirect
    ta.token = msg["token"]
    ta.payment_method_name = "Paytrail"
    ta.save()

    # All done, redirect user
    return msg["url"]


def handle_failure(request: HttpRequest) -> HttpResponse:
    """Handles failure message from paytrail"""

    # Get parameters
    order_number = request.GET.get("ORDER_NUMBER", "")
    timestamp = request.GET.get("TIMESTAMP", "")
    authcode = request.GET.get("RETURN_AUTHCODE", "")
    secret = settings.PAYTRAIL_SECRET

    # Validate, and mark transaction as cancelled
    if paytrail.validate_failure(order_number, timestamp, authcode, secret):
        ta = get_object_or_404(StoreTransaction, pk=int(order_number))
        ta_common.handle_cancellation(ta)
        return HttpResponseRedirect(reverse("store:pm:paytrail-failure"))

    return render(request, "store/failure.html")


def handle_success(request: HttpRequest) -> HttpResponse:
    """Handles the success user redirect from Paytrail"""

    # Get parameters
    order_number = request.GET.get("ORDER_NUMBER", "")
    timestamp = request.GET.get("TIMESTAMP", "")
    paid = request.GET.get("PAID", "")
    method = request.GET.get("METHOD", "")
    authcode = request.GET.get("RETURN_AUTHCODE", "")
    secret = settings.PAYTRAIL_SECRET

    # Validate, and mark transaction as pending
    if paytrail.validate_success(order_number, timestamp, paid, method, authcode, secret):
        ta = get_object_or_404(StoreTransaction, pk=int(order_number))
        ta_common.handle_pending(ta)
        return HttpResponseRedirect(reverse("store:pm:paytrail-success"))

    return render(request, "store/success.html")


def handle_notify(request: HttpRequest) -> HttpResponse:
    """Handles the actual success notification from Paytrail"""

    # Get parameters
    order_number = request.GET.get("ORDER_NUMBER", "")
    timestamp = request.GET.get("TIMESTAMP", "")
    paid = request.GET.get("PAID", "")
    method = request.GET.get("METHOD", "")
    authcode = request.GET.get("RETURN_AUTHCODE", "")
    secret = settings.PAYTRAIL_SECRET

    # Validate & handle
    if paytrail.validate_success(order_number, timestamp, paid, method, authcode, secret):
        # Get transaction
        ta = get_object_or_404(StoreTransaction, pk=int(order_number))
        if ta.is_paid:
            logger.warning("Somebody is trying to pay an already paid transaction (%s).", ta.id)
            return HttpResponse("")

        # Use common functions to handle the payment
        # If handling the payment fails, cause 404.
        # This will tell paytrail to try notifying again later.
        if not ta_common.handle_payment(request, ta):
            raise Http404
    else:
        logger.warning("Error while attempting to validate paytrail notification!")
        raise Http404

    # Just respond with something
    return HttpResponse("")
