import logging

import arrow
from django.conf import settings
from django.db.models import Q
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone

from Instanssi.common.auth import infodesk_access_required
from Instanssi.infodesk.forms import ItemKeyScanForm, TransactionKeyScanForm
from Instanssi.store.models import StoreTransaction, TransactionItem

logger = logging.getLogger(__name__)

TXN_PREFIX = "transaction:"
TXN_ITEM_PREFIX = "item:"


@infodesk_access_required
def index(request: HttpRequest) -> HttpResponse:
    """Main infodesk view."""
    return render(request, "infodesk/index.html", {})


def ta_fuzzy_query(term: str) -> Q:
    """Generate a fuzzy query filter for finding StoreTransactions."""
    return Q(lastname__icontains=term) | Q(firstname__icontains=term) | Q(key__istartswith=term)


def ti_fuzzy_query(term: str) -> Q:
    """Generate a fuzzy query filter for finding TransactionItems."""
    return Q(key__istartswith=term)


@infodesk_access_required
def order_search_ac(request: HttpRequest) -> HttpResponse:
    """Autocomplete suggestions for the infodesk general purpose search.

    Each suggestion's "id" should find something in the order_search view.
    """
    term = request.GET.get("term")
    if not term:
        raise Http404

    # find transactions that contain the search term
    transactions = StoreTransaction.objects.filter(ta_fuzzy_query(term))
    items = TransactionItem.objects.filter(ti_fuzzy_query(term))

    def fmt_t(t):
        return arrow.get(t).to(settings.TIME_ZONE).format("DD.MM.YYYY HH:mm")

    def format_transaction(t):
        return "%s, %s (%s)" % (t.lastname, t.firstname, fmt_t(t.time_created))

    results = [
        {"id": "%s%s" % (TXN_PREFIX, t.id), "text": format_transaction(t)}  # exact query link
        for t in transactions
    ]

    results.extend(
        [
            {
                "id": "%s%s" % (TXN_ITEM_PREFIX, item.key),
                "text": "%s -- ostaja %s" % (item.item, format_transaction(item.transaction)),
            }
            for item in items
        ]
    )

    return JsonResponse({"more": False, "results": results})


@infodesk_access_required
def order_search(request):
    """Search view that finds transactions, items and customers."""
    term = request.GET.get("term")
    transactions = None
    items = None

    if term:
        # If the user got here through the autocomplete JS, 'term' will
        # be a full transaction or item id with a prefix.
        # If the JS has failed, just behave like its fuzzy autocomplete search.

        item_filter = None
        txn_filter = None

        # FIXME: Even a regex might look cleaner than this.
        if term.startswith(TXN_PREFIX):
            txn_id = term[len(TXN_PREFIX):]
            if txn_id.isdigit():
                txn_filter = Q(id__exact=txn_id)
        if term.startswith(TXN_ITEM_PREFIX):
            item_filter = Q(key__exact=term[len(TXN_ITEM_PREFIX):])

        # If we don't have a more specific filter, just show all fuzzy results
        if not txn_filter:
            txn_filter = ta_fuzzy_query(term)

        if not item_filter:
            item_filter = ti_fuzzy_query(term)

        transactions = StoreTransaction.objects.filter(txn_filter)
        items = TransactionItem.objects.filter(item_filter)

    return render(
        request, "infodesk/order_search.html", {"transactions": transactions, "items": items, "term": term}
    )


@infodesk_access_required
def item_check(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ItemKeyScanForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse("infodesk:item_info", args=(form.item.id,)))
    else:
        form = ItemKeyScanForm()

    return render(request, "infodesk/item_check.html", {"form": form})


@infodesk_access_required
def transaction_check(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = TransactionKeyScanForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse("infodesk:transaction_info", args=(form.transaction.id,)))
    else:
        form = TransactionKeyScanForm()

    return render(request, "infodesk/ta_check.html", {"form": form})


@infodesk_access_required
def item_mark(request: HttpRequest, item_id: int) -> HttpResponse:
    """Mark an item as delivered."""
    item = get_object_or_404(TransactionItem, pk=item_id)
    item.time_delivered = timezone.now()
    item.save()
    if item.transaction.is_paid:
        logger.info("Item %d marked as delivered.", item.id, extra={"user": request.user})
    else:
        logger.info(
            "Item %d marked as delivered (no payment recorded!)", item.id, extra={"user": request.user}
        )

    return HttpResponseRedirect(reverse("infodesk:item_info", args=(item.id,)))


@infodesk_access_required
def item_info(request: HttpRequest, item_id: int) -> HttpResponse:
    item = get_object_or_404(TransactionItem, pk=item_id)
    return render(request, "infodesk/item_info.html", {"item": item})


@infodesk_access_required
def transaction_info(request: HttpRequest, transaction_id: int) -> HttpResponse:
    transaction = get_object_or_404(StoreTransaction, pk=transaction_id)
    return render(request, "infodesk/ta_info.html", {"transaction": transaction})
