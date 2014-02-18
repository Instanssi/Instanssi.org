# -*- coding: utf-8 -*-

from datetime import datetime
import random
import time

from django.db import transaction, IntegrityError
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404

from common.misc import get_url
from Instanssi.store.utils import bitpay
from Instanssi.store.models import StoreItem, StoreTransaction, TransactionItem
from Instanssi.store.utils.emailer import ReceiptMailer

# Logging related
import logging
logger = logging.getLogger(__name__)

def start_process(ta):
    """This should be used to start the bitpay payment process. Will redirect as necessary."""
    
    product_list = []
    total = 0

    for item in TransactionItem.get_distinct_storeitems(ta):
        amount = TransactionItem.get_transaction_item_amount(ta, item)
        total += amount * item.price

    # Skip extra personal information because Bitpay doesn't require them
    data = {
        'price': str(total),
        'currency': 'EUR',
        'posData': {
            'transaction_id': str(ta.id),
            'transaction_key': ta.key,
        }, 
        'notificationURL': get_url(reverse('store:pm:bitpay-notify')),
        'transactionSpeed': settings.BITPAY_SPEED,
        'notificationEmail': settings.BITPAY_EMAIL,
        'redirectURL': get_url(reverse('store:pm:bitpay-success')),
        'buyerName': ta.firstname + ' ' + ta.lastname,
        'buyerEmail': ta.email
    }

    # Make a request
    msg = None
    try:
        msg = bitpay.request(settings.BITPAY_KEY, data)
    except bitpay.BitpayException as ex:
        a, b = ex.args
        logger.error('(%s) %s' % (b, a))
        return HttpResponseRedirect(reverse('store:pm:bitpay-failure'))
    except Exception as ex:
        logger.error('%s.' % (ex))
        return HttpResponseRedirect(reverse('store:pm:bitpay-failure'))

    # Save token, redirect
    ta.token = msg['id']
    ta.save()

    # All done, redirect user
    return HttpResponseRedirect(msg['url'])

def handle_failure(request):
    """ Handles failure message caused by exceptions """
    
    # FIXME this never comes from bitpay but is here because of
    # mysterious Exception redirects in previous function.

    return render_to_response('store/failure.html')
        
def handle_success(request):
    """ Handles the success user redirect from Paytrail """
    return render_to_response('store/success.html')

def handle_notify(request):
    """ Handles the actual success notification from Paytrail """
    
    # Get data, and make sure it looks right
    try:
        data = json.loads(request.raw_post_data)
        transaction_id = int(data['posData']['transaction_id'])
        transaction_key = data['posData']['transaction_key']
        bitpay_id = data['id']
        status = data['status']
    except:
        raise Http404
    
    # Try to find correct transaction
    # If transactions is not found, this will throw 404.
    ta_is_valid = False
    try:
        ta = StoreTransaction.objects.get(pk=transaction_id, key=transaction_key, token=bitpay_id)
        ta_is_valid = True
    except StoreTransaction.DoesNotExist:
        logger.warning("Error while attempting to validate bitpay notification!")
        raise Http404
        
    if ta_is_valid:
        if status == 'confirmed':
            ta.time_paid = datetime.now()
            ta.save()
            pass
            
        if status == 'paid':
            # Paid but not confirmed
            pass
            
        if status == 'expired':
            # Paument expired, assume cancelled
            pass

    # Just respond with something
    return HttpResponse("")
