# -*- coding: utf-8 -*-

from datetime import datetime
from django.db import transaction
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from common.responses import JSONResponse
#from Instanssi.settings import SVM_ID, SVM_SECRET
from Instanssi.store.svmlib import svm_request
from Instanssi.store.forms import StoreOrderForm
from Instanssi.store.models import StoreItem, StoreTransaction, TransactionItem

# Logging related
import logging
logger = logging.getLogger(__name__)


# Shows a simple error message
def error_page(request):
    return render_to_response('store/error.html', {
    }, context_instance=RequestContext(request))


# Shows a simple success message
def success_page(request):
    return render_to_response('store/success.html', {
    }, context_instance=RequestContext(request))


# Handles the actual success notification from SVM
def notify_handler(request):
    return JSONResponse({})


# Should take care of JSON request from our own form, and then make the
# request to Suomen verkkomaksut JSON api.
def transaction_handler(request):
    return JSONResponse({'error': 'Method has not been implemented.'})


# Does some initial wrangling of the store requests.
@transaction.commit_on_success
def purchase_handler(request):
    if request.method == 'POST':
        transaction_form = StoreOrderForm(request.POST)
        if transaction_form.is_valid():
            new_transaction = transaction_form.save(commit=False)
            new_transaction.time = datetime.now()
            new_transaction.save()

            # create TransactionItems for each item
            post_items = filter(
                lambda (k, v): k.startswith("item-") and k[5:] and v,
                request.POST.items()
            )
            items = [(k[5:], v) for (k, v) in post_items]

            transaction_items = []

            for (item_id, amount) in items:
                store_item = StoreItem.objects.get(id=int(item_id))
                new_item = TransactionItem(
                    item=store_item,
                    transaction=new_transaction,
                    amount=amount
                )
                new_item.save()
                transaction_items.append(new_item)

            # call Suomen Verkkomaksut API (TODO!)
            #message = svm_query(SVM_ID, SVM_SECRET,

            # redirect user to SV
            # ... or not. Waiting for implementation.
            return JSONResponse({
                'error': 'Unimplemented! We got your data though.'
            })
    else:
        transaction_form = StoreOrderForm()

    # Copypasta from Instanssi.main2013.views
    templatename = 'liput'
    return render_to_response('main2013/' + templatename + '.html', {
        'event_id': 5,
        'templatename': templatename,
        'transaction_form': transaction_form
    }, context_instance=RequestContext(request))
