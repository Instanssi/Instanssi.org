# -*- coding: utf-8 -*-

from datetime import datetime
from django.db import transaction
from django.conf import settings
from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from Instanssi.store.svmlib import svm_validate
from Instanssi.store.forms import StoreOrderForm
from Instanssi.store.models import StoreItem, StoreTransaction, TransactionItem

# Logging related
import logging
logger = logging.getLogger(__name__)

# Handles the actual success notification from SVM
def notify_handler(request):
    # Get parameters
    order_number = request.GET.get('ORDER_NUMBER', '')
    timestamp = request.GET.get('TIMESTAMP', '')
    paid = request.GET.get('PAID', '')
    method = request.GET.get('METHOD', '')
    authcode = request.GET.get('RETURN_AUTHCODE', '')
    secret = settings.VMAKSUT_SECRET
    
    # Validata & handle
    if svm_validate(order_number, timestamp, paid, method, authcode, secret):
        ta = get_object_or_404(StoreTransaction, pk=int(order_number))
        if ta.paid:
            raise Http404
        ta.time_paid = datetime.now()
        ta.save()
    else:
        logger.warning("Error while attempting to validate svm notification!")
        raise Http404
        
    # Just respond with something
    return HttpResponse("")
