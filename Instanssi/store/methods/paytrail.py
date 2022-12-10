import logging
from contextlib import contextmanager
from typing import Generator, List

from django.conf import settings
from django.db.transaction import atomic
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from yarl import URL

from Instanssi.store.models import StoreTransaction, StoreTransactionEvent
from Instanssi.store.utils import ta_common
from Instanssi.store.utils.paytrail import (
    Address,
    CallbackUrl,
    Customer,
    Item,
    NewPaymentCallback,
    NewPaymentStatus,
    Payment,
    PaymentMethod,
    PaytrailError,
    create_payment,
    verify_callback,
)

logger = logging.getLogger(__name__)


def start_process(request: HttpRequest, transaction: StoreTransaction) -> str:
    api_url = URL(settings.PAYTRAIL_V2_API_URL)
    merchant_id = settings.PAYTRAIL_V2_ID
    secret = settings.PAYTRAIL_V2_SECRET

    product_list: List[Item] = []
    total: int = 0
    for store_item, item_variant, purchase_price in transaction.get_distinct_store_items_and_prices():
        count = transaction.get_store_item_count(
            store_item, variant=item_variant, purchase_price=purchase_price
        )
        unit_price = int(purchase_price * 100)
        total += unit_price * count
        product_list.append(
            Item(
                description=f"{store_item.name}, {item_variant.name}" if item_variant else store_item.name,
                product_code=f"{store_item.id}:{item_variant.id}" if item_variant else str(store_item.id),
                unit_price=unit_price,
                units=count,
                vat_percentage=0,
            )
        )

    success_callback_uri = reverse("store:pm:paytrail-callback")
    cancel_callback_uri = reverse("store:pm:paytrail-callback")
    success_redirect_uri = reverse("store:pm:paytrail-redirect-success")
    cancel_redirect_uri = reverse("store:pm:paytrail-redirect-cancel")
    payment = Payment(
        amount=total,
        currency="EUR",
        language="FI",
        reference=str(transaction.id),
        stamp=str(transaction.id),
        callback_urls=CallbackUrl(
            success=URL(request.build_absolute_uri(success_callback_uri)),
            cancel=URL(request.build_absolute_uri(cancel_callback_uri)),
        ),
        redirect_urls=CallbackUrl(
            success=URL(request.build_absolute_uri(success_redirect_uri)),
            cancel=URL(request.build_absolute_uri(cancel_redirect_uri)),
        ),
        customer=Customer(
            phone=transaction.telephone,
            email=transaction.email,
            first_name=transaction.firstname,
            last_name=transaction.lastname,
            company_name=transaction.company,
        ),
        invoicing_address=Address(
            street_address=transaction.street,
            postal_code=transaction.postalcode,
            city=transaction.city,
            country=transaction.country.code,
        ),
        items=product_list,
    )

    try:
        response = create_payment(api_url, merchant_id, secret, payment, groups=[PaymentMethod.BANK])
    except Exception as e:
        logger.exception("Payment request to paytrail failed: %s", e)
        return reverse("store:pm:paytrail-cancel")

    # Save transaction log
    StoreTransactionEvent.log(
        transaction,
        "Payment created",
        dict(transaction_id=response.transaction_id, request_id=response.request_id),
    )

    # Save transaction ID and payment method
    transaction.token = response.transaction_id
    transaction.payment_method_name = "Paytrail"
    transaction.save()

    # All done, redirect user
    return response.href


def verify_request(request: HttpRequest) -> NewPaymentCallback:
    """Verifies a request coming from paytrail. May raise exceptions!"""
    try:
        return verify_callback(
            params=request.GET.dict(),
            account=settings.PAYTRAIL_V2_ID,
            secret=settings.PAYTRAIL_V2_SECRET,
        )
    except PaytrailError as e:
        logger.exception("Paytrail made a faulty request", exc_info=e)
        raise


@contextmanager
def run_atomic(callback: NewPaymentCallback) -> Generator[StoreTransaction, None, None]:
    transaction_id = int(callback.stamp)
    with atomic():
        transaction = StoreTransaction.objects.select_for_update().get(pk=transaction_id)
        yield transaction


def handle_redirect_success(request: HttpRequest) -> HttpResponse:
    """
    Handles success redirect from paytrail, verifies the data, and redirects to our own success page.
    We do a redirect to get rid of the crap in GET params.
    """
    callback = verify_request(request)
    with run_atomic(callback) as transaction:
        StoreTransactionEvent.log(transaction, "Success redirect", callback.to_dict())
    return HttpResponseRedirect(reverse("store:pm:paytrail-success"))


def handle_redirect_cancel(request: HttpRequest) -> HttpResponse:
    """
    Handles cancel redirect from paytrail, verifies the data, and redirects to our own cancellation page.
    We do a redirect to get rid of the crap in GET params.
    """
    callback = verify_request(request)
    with run_atomic(callback) as transaction:
        StoreTransactionEvent.log(transaction, "Cancel redirect", callback.to_dict())
    return HttpResponseRedirect(reverse("store:pm:paytrail-cancel"))


def handle_callback(request: HttpRequest) -> HttpResponse:
    """Handles any success/cancel callback from paytrail"""
    callback = verify_request(request)
    with run_atomic(callback) as transaction:
        StoreTransactionEvent.log(transaction, "Callback", callback.to_dict())
        if callback.status == NewPaymentStatus.OK:
            ta_common.handle_payment(request, transaction)
        elif callback.status == NewPaymentStatus.FAIL:
            ta_common.handle_cancellation(transaction)
        else:
            ta_common.handle_pending(transaction)
    return JsonResponse({})


def handle_cancel(request: HttpRequest) -> HttpResponse:
    """Just renders the static failure page"""
    return render(request, "store/failure.html")


def handle_success(request: HttpRequest) -> HttpResponse:
    """Just renders the static success page"""
    return render(request, "store/success.html")
