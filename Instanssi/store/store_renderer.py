# -*- coding: utf-8 -*-

from datetime import datetime
from django.db import transaction
from django.template import RequestContext
from common.responses import JSONResponse
from Instanssi.store.svmlib import svm_request
from Instanssi.store.forms import StoreOrderForm
from Instanssi.store.models import StoreItem, StoreTransaction, TransactionItem

def render_store(request, event_id):
    if request.method == 'POST':
        transaction_form = StoreOrderForm(request.POST, event_id=event_id)

        if transaction_form.is_valid():
            new_transaction = transaction_form.save()

            # call Suomen Verkkomaksut API (TODO!)
            #message = svm_query(SVM_ID, SVM_SECRET,

            # redirect user to SV
            # ... or not. Waiting for implementation.
            return JSONResponse({
                'error': 'Unimplemented! We got your data though.'
            })
            
            # Redirect
            #return HttpResponseRedirect("")
    else:
        transaction_form = StoreOrderForm(event_id=event_id)
        
    return {'transaction_form': transaction_form}