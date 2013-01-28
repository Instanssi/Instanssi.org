# -*- coding: utf-8 -*-

from datetime import datetime
import hashlib
import time
from django.db import transaction
from django.conf import settings
from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from Instanssi.store.svmlib import svm_validate
from Instanssi.store.forms import StoreOrderForm
from Instanssi.store.models import StoreItem, StoreTransaction, TransactionItem
from Instanssi.tickets.models import Ticket

# Logging related
import logging
logger = logging.getLogger(__name__)

def gen_sha(text):
    h = hashlib.sha1()
    h.update(text)
    return h.hexdigest()

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
        ta.key = gen_sha('%s|%s|%s' % (ta.id, ta.token, time.time()))
        ta.save()
        
        # Generate ticket information for tickets
        for titem in TransactionItem.objects.filter():
            if titem.item.delivery_type == 1:
                for i in range(titem.amount):
                    ticket = Ticket()
                    ticket.key = gen_sha('%s|%s|%s|%s|%s' % (i, titem.id, titem.item.id, ta.token, time.time()))
                    ticket.transaction = ta
                    ticket.storeitem = titem.item
                    ticket.event = titem.item.event
                    ticket.owner_firstname = ta.firstname
                    ticket.owner_lastname = ta.lastname
                    ticket.owner_email = ta.email
                    ticket.save()
    else:
        logger.warning("Error while attempting to validate svm notification!")
        raise Http404
        
    # Just respond with something
    return HttpResponse("")
