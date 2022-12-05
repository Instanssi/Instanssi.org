from django.http import HttpRequest
from django.shortcuts import render
from django.urls import reverse

from Instanssi.store.models import StoreTransaction
from Instanssi.store.utils import ta_common


def start_process(request: HttpRequest, ta: StoreTransaction) -> str:
    """
    No payment method was required, so just mark everything done right away.
    """

    # Since no payment is required, just mark everything done right away
    ta.payment_method_name = "No payment"
    ta.save()
    ta.refresh_from_db()

    ta_common.handle_payment(request, ta)

    # All done, redirect user
    return reverse("store:pm:no-method-success")


def handle_success(request):
    return render(request, "store/success.html")
