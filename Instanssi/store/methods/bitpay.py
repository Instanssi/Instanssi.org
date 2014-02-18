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

    data = {
        'price': str(total),
        'currency': 'EUR',
        'posData': str(ta.id),
        'notificationURL': get_url(reverse('store:pm:bitpay-notify')),
        'transactionSpeed': settings.BITPAY_SPEED,
        'notificationEmail': settings.BITPAY_EMAIL,
        'redirectURL': get_url(reverse('store:pm:bitpay-success')),
        'buyerName': ta.firstname + ' ' + ta.lastname,
        'buyerEmail': ta.email
        # Skip extra personal information because Bitpay doesn't require them
        },
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
    ta.token = msg['token']
    ta.save()

    # All done, redirect user
    return HttpResponseRedirect(msg['url'])

def handle_failure(request):
    """ Handles failure message from bitpay """
    
    # FIXME this never comes from bitpay but is here because of
    # mysterious Exception redirects in previous function.
    # Currently contains some fluff from paytrail module

    # Get parameters
    order_number = request.GET.get('ORDER_NUMBER', '')
    timestamp = request.GET.get('TIMESTAMP', '')
    authcode = request.GET.get('RETURN_AUTHCODE', '')
    secret = settings.VMAKSUT_SECRET
    
    # Validate, and mark transaction as cancelled
    if paytrail.validate_failure(order_number, timestamp, authcode, secret):
        try:
            ta = StoreTransaction.objects.get(pk=int(order_number))
            ta.time_cancelled = datetime.now()
            ta.save()
        except:
            pass

    return render_to_response('store/failure.html')
        
def handle_success(request):
    """ Handles the success user redirect from Paytrail """
    return render_to_response('store/success.html')

def handle_notify(request):
    """ Handles the actual success notification from Paytrail """
    res = request.getresponse()
    message = json.loads(res.read())

    if message.status != 'confirmed':
        # Not paid yet or gets expired or something...

    # Get parameters
    timestamp =  message.currentTime # TODO milliseconds, is this OK

    # FIXME unmodified paytrail stuff..

    order_number = request.GET.get('ORDER_NUMBER', '')
    paid = request.GET.get('PAID', '')
    method = request.GET.get('METHOD', '')
    authcode = request.GET.get('RETURN_AUTHCODE', '')
    secret = settings.VMAKSUT_SECRET

    # Validata & handle
    if paytrail.validate_success(order_number, timestamp, paid, method, authcode, secret):
        # Get transaction
        ta = get_object_or_404(StoreTransaction, pk=int(order_number))
        if ta.is_paid:
            logger.warning('Somebody is trying to pay an already paid transaction (%s).' % (ta.id))
            raise Http404

        # Deliver email.
        mailer = ReceiptMailer('"Instanssi" <noreply@'+settings.DOMAIN+'>', ta.email, 'Instanssi.org kuitti')
        mailer.ordernumber(ta.id)
        mailer.firstname(ta.firstname)
        mailer.lastname(ta.lastname)
        mailer.email(ta.email)
        mailer.company(ta.company)
        mailer.mobile(ta.mobile)
        mailer.telephone(ta.telephone)
        mailer.street(ta.street)
        mailer.city(ta.city)
        mailer.postalcode(ta.postalcode)
        mailer.country(ta.country)
        
        # Add items to email
        for item in TransactionItem.get_distinct_storeitems(ta):
            amount = TransactionItem.get_transaction_item_amount(ta, item)
            mailer.add_item(item.id, item.name, item.price, amount)

        # Form transaction url
        transaction_url = get_url(reverse('store:ta_view', args=(ta.key,)))
        mailer.transactionurl(transaction_url)
            
        # Send mail
        try:
            mailer.send()
        except Exception as ex:
            logger.error('%s.' % (ex))
            raise Http404
        
        # Mark as paid
        ta.time_paid = datetime.now()
        ta.save()
    else:
        logger.warning("Error while attempting to validate paytrail notification!")
        raise Http404
        
    # Just respond with something
    return HttpResponse("")
