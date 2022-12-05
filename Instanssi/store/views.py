import logging

from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import never_cache
from django.utils import timezone

from Instanssi.store.models import StoreTransaction, TransactionItem

logger = logging.getLogger(__name__)


def has_infodesk_access(request: HttpRequest) -> bool:
    return (
        request.user.is_authenticated
        and request.user.is_active
        and request.user.has_perm("store.change_storetransaction")
    )


def mark_item_delivered(request: HttpRequest, item_key: str) -> None:
    if not has_infodesk_access(request):
        raise PermissionDenied()

    item = TransactionItem.objects.get(key=item_key)
    item.time_delivered = timezone.now()
    item.save()


def handle_status_update(request: HttpRequest) -> None:
    if request.method == "POST":
        item_key = request.POST.get("ta_item_key")
        if item_key:
            mark_item_delivered(request, item_key)


@never_cache
def ta_view(request: HttpRequest, transaction_key: str) -> HttpResponse:
    """Displays the details of a specific transaction."""

    handle_status_update(request)

    transaction = get_object_or_404(StoreTransaction, key=transaction_key)
    if not transaction.is_paid:
        raise Http404

    ta_items = TransactionItem.objects.filter(transaction=transaction)
    res = render(
        request,
        "store/transaction.html",
        {
            "transaction": transaction,
            "ta_items": ta_items,
            "has_infodesk_access": has_infodesk_access(request),
        },
    )
    return res


@never_cache
def ti_view(request: HttpRequest, item_key: str) -> HttpResponse:
    """Displays the details of a specific purchased item."""

    handle_status_update(request)

    ta_item = get_object_or_404(TransactionItem, key=item_key)
    if not ta_item.transaction.is_paid:
        raise Http404

    res = render(
        request,
        "store/transaction_item.html",
        {
            "ta_item": ta_item,
            "has_infodesk_access": has_infodesk_access(request),
        },
    )
    return res
