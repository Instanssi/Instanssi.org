# -*- coding: utf-8 -*-

from datetime import datetime

from django.db.models import Q
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect,Http404
from django.core.urlresolvers import reverse

from common.responses import JSONResponse
from Instanssi.infodesk.misc.auth_decorator import infodesk_access_required
from Instanssi.infodesk.forms import TransactionKeyScanForm, ItemKeyScanForm
from Instanssi.store.models import StoreTransaction, TransactionItem

# Logging related
import logging
logger = logging.getLogger(__name__)


@infodesk_access_required
def index(request):
    return render_to_response('infodesk/index.html', {}, context_instance=RequestContext(request))

@infodesk_access_required
def ta_lookup_autocomplete(request):
    try:
        lookup = request.GET['term']
    except:
        raise Http404

    # lookup name in people who have bought something
    txns = StoreTransaction.objects.filter(
        Q(lastname__icontains=lookup) | Q(firstname__icontains=lookup))
    return JSONResponse(['%s, %s' % (t.lastname, t.firstname) for t in txns])


@infodesk_access_required
def ta_lookup(request):
    # The form autocompletes names like "lastname, firstname"
    # If somebody wrote a comma in their name, they can buy a new ticket.
    # We could also accept ids (with some potential UI problems).
    firstname = None
    lastname = None

    try:
        names = request.GET['name']
        name = names.split(',')
        lastname = name[0]
        firstname = name[1].lstrip()
    except:
        raise Http404

    storetransactions = StoreTransaction.objects.filter(
        lastname=lastname,
        firstname=firstname
    )

    return render_to_response('infodesk/ta_lookup.html', {
        'transactions': storetransactions,
        'name': names
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
    if item.transaction.is_paid:
        item.time_delivered = datetime.now()
        item.save()
        logger.info('Item %d marked as delivered.' % (item.id,), extra={'user': request.user})
    return HttpResponseRedirect(reverse('infodesk:index'))


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
