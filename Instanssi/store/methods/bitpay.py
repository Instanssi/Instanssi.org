# -*- coding: utf-8 -*-

import json
from Instanssi.common.misc import get_url
from django.conf import settings
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, Http404
from django.shortcuts import render
from Instanssi.store.models import StoreTransaction
from Instanssi.store.utils import bitpay, ta_common

# Logging related
import logging
logger = logging.getLogger(__name__)


def start_process(ta):
    """This should be used to start the bitpay payment process. Will redirect as necessary."""
    
    # Skip extra personal information because Bitpay doesn't require them
    data = {
        'price': str(ta.get_total_price()),
        'currency': 'EUR',
        'posData': str(ta.id),
        'fullNotifications': True, 
        'notificationURL': get_url(reverse('store:pm:bitpay-notify')),
        'transactionSpeed': settings.BITPAY_SPEED,
        'notificationEmail': settings.BITPAY_EMAIL,
        'redirectURL': get_url(reverse('store:pm:bitpay-success')),
        'buyerName': ta.firstname + ' ' + ta.lastname,
        'buyerEmail': ta.email
    }

    # Make a request
    try:
        msg = bitpay.request(settings.BITPAY_KEY, data)
    except bitpay.BitpayException as ex:
        a, b = ex.args
        logger.error('(%s) %s', b, a)
        return reverse('store:pm:bitpay-failure')
    except Exception as ex:
        logger.error('%s.', ex)
        return reverse('store:pm:bitpay-failure')

    # Save token, redirect
    ta.token = msg['id']
    ta.payment_method_name = 'Bitpay'
    ta.save()

    # All done, redirect user
    return msg['url']


def handle_failure(request):
    """ Handles failure message caused by exceptions """
    
    # FIXME this never comes from bitpay but is here because of
    # mysterious Exception redirects in previous function.
    return render(request, 'store/failure.html')


def handle_success(request):
    """ Handles the success user redirect from Paytrail """
    return render(request, 'store/success.html')


@csrf_exempt
def handle_notify(request):
    """ Handles the actual success notification from Paytrail """
    
    # Get data, and make sure it looks right
    try:
        data = json.loads(request.body)
        transaction_id = int(data['posData'])
        bitpay_id = data['id']
        status = data['status']
    except Exception as ex:
        logger.error("%s.", ex)
        raise Http404
    
    # Try to find correct transaction
    # If transactions is not found, this will throw 404.
    try:
        ta = StoreTransaction.objects.get(pk=transaction_id, token=bitpay_id)
    except StoreTransaction.DoesNotExist:
        logger.warning("Error while attempting to validate bitpay notification!")
        raise Http404

    # If transaction is paid and confirmed, stop here.
    if ta.is_paid:
        return HttpResponse("")

    # We have a valid transaction. Do something about it.
    if status == 'confirmed' or status == 'complete':
        # Paid and confirmed.
        if not ta_common.handle_payment(ta):
            raise Http404
        return HttpResponse("")

    if status == 'paid':
        # Paid but not confirmed
        ta_common.handle_pending(ta)
        return HttpResponse("")

    if status == 'expired':
        # Payment expired, assume cancelled
        ta_common.handle_cancellation(ta)
        return HttpResponse("")

    logger.warning("Unhandled bitpay notification '%s' for id %d.", status, ta.id)

    # Just respond with something
    return HttpResponse("")
