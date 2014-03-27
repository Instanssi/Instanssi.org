# -*- coding: utf-8 -*-

from datetime import datetime

from common.auth import infodesk_access_required

from django.db.models import Q
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse

from common.responses import JSONResponse
from Instanssi.infodesk.forms import TransactionKeyScanForm, ItemKeyScanForm
from Instanssi.store.models import StoreTransaction, TransactionItem

# Logging related
import logging
logger = logging.getLogger(__name__)


@infodesk_access_required
def index(request):
    return render_to_response('infodesk/index.html', {}, context_instance=RequestContext(request))


def ta_fuzzy_query(term):
    """Returns a fuzzy query filter for finding StoreTransactions."""
    return (
        Q(lastname__icontains=term) |
        Q(firstname__icontains=term) |
        Q(key__istartswith=term))


def ti_fuzzy_query(term):
    """Returns a fuzzy query filter for finding TransactionItems."""
    return Q(key__istartswith=term)


@infodesk_access_required
def order_search_ac(request):
    """This view provides autocomplete suggestions for the infodesk
    general purpose search search. Each suggestion's key should find
    something on the proper search page"""

    term = request.GET.get('term')
    if not term:
        raise Http404

    # find transactions that contain the search term
    txns = StoreTransaction.objects.filter(ta_fuzzy_query(term))
    items = TransactionItem.objects.filter(ti_fuzzy_query(term))

    fmt_t = lambda t: t.strftime('%d.%m.%Y %H:%M')

    def format_transaction(t):
        return '%s, %s (%s)' % (t.lastname, t.firstname, fmt_t(t.time_created))

    results = [{
        'id': t.id,
        'text': format_transaction(t)
    } for t in txns]

    results.extend([{
        'id': item.key,
        'text': '%s -- ostaja %s' % (item.item, format_transaction(item.transaction))
    } for item in items])

    return JSONResponse({
        'more': False,
        'results': results
    })


@infodesk_access_required
def order_search(request):
    """This view is used to search for transactions or customers."""

    term = request.GET.get('term')
    txns = None
    items = None

    if term:
        # If the user got here through the autocomplete JS, 'term' will
        # be a full transaction id. If the JS doesn't work, this should
        # perform the fuzzy search instead.

        txn_filter = ta_fuzzy_query(term)
        item_filter = ti_fuzzy_query(term)

        if term.isdigit():
            txn_filter = txn_filter | Q(id__exact=term)

        txns = StoreTransaction.objects.filter(txn_filter)
        items = TransactionItem.objects.filter(item_filter)

    return render_to_response('infodesk/order_search.html', {
        'transactions': txns,
        'items': items,
        'term': term
    }, context_instance=RequestContext(request))


@infodesk_access_required
def item_check(request):
    if request.method == 'POST':
        form = ItemKeyScanForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('infodesk:item_info', args=(form.item.id,)))
    else:
        form = ItemKeyScanForm()

    return render_to_response('infodesk/item_check.html', {
        'form': form
    }, context_instance=RequestContext(request))


@infodesk_access_required
def transaction_check(request):
    if request.method == 'POST':
        form = TransactionKeyScanForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('infodesk:transaction_info', args=(form.transaction.id,)))
    else:
        form = TransactionKeyScanForm()

    return render_to_response('infodesk/ta_check.html', {
        'form': form
    }, context_instance=RequestContext(request))


@infodesk_access_required
def item_mark(request, item_id):
    item = get_object_or_404(TransactionItem, pk=item_id)
    item.time_delivered = datetime.now()
    item.save()
    if item.transaction.is_paid:
        logger.info('Item %d marked as delivered.' % (item.id,), extra={'user': request.user})
    else:
        logger.info(
            'Item %d marked as delivered (no payment recorded!)'
            % (item.id,), extra={'user': request.user})

    return HttpResponseRedirect(
        reverse('infodesk:item_info', args=(item.id,)))


@infodesk_access_required
def item_info(request, item_id):
    item = get_object_or_404(TransactionItem, pk=item_id)
    return render_to_response('infodesk/item_info.html', {
        'item': item
    }, context_instance=RequestContext(request))


@infodesk_access_required
def transaction_info(request, transaction_id):
    transaction = get_object_or_404(StoreTransaction, pk=transaction_id)
    return render_to_response('infodesk/ta_info.html', {
        'transaction': transaction
    }, context_instance=RequestContext(request))
