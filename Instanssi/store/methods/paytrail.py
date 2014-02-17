# -*- coding: utf-8 -*-

from datetime import datetime
import random
import time

from django.db import transaction, IntegrityError
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404

from Instanssi.store.utils import paytrail
from Instanssi.store.models import StoreItem, StoreTransaction, TransactionItem
from Instanssi.store.utils.emailer import ReceiptMailer

# Logging related
import logging
logger = logging.getLogger(__name__)

def get_url(path):
    proto = 'https://' if settings.SSL_ON else 'http://'
    host = settings.DOMAIN
    return '%s%s%s' % (proto, host, path or '')

def start_process(ta):
    product_list = []

    for item in TransactionItem.get_distinct_storeitems(ta):
        amount = TransactionItem.get_transaction_item_amount(ta, item)
        product_list.append({
            'title': item.name,
            'code': str(item.id),
            'amount': str(amount),
            'price': str(item.price),
            'vat': '0',
            'type': 1,
        })

    data = {
        'orderNumber': str(ta.id),
        'currency': 'EUR',
        'locale': 'fi_FI',
        'urlSet': {
            'success': get_url(reverse('store:pm:paytrail-success')),
            'failure': get_url(reverse('store:pm:paytrail-failure')),
            'notification': get_url(reverse('store:pm:paytrail-notify')),
            'pending': '',
        },
        'orderDetails': {
            'includeVat': 1,
            'contact': {
                'telephone': ta.telephone,
                'mobile': ta.mobile,
                'email': ta.email,
                'firstName': ta.firstname,
                'lastName': ta.lastname,
                'companyName': ta.company,
                'address': {
                    'street': ta.street,
                    'postalCode': ta.postalcode,
                    'postalOffice': ta.city,
                    'country': ta.country.code
                }
            },
            'products': product_list,
        },
    }

    # Make a request
    msg = None
    try:
        msg = paytrail.request(settings.VMAKSUT_ID, settings.VMAKSUT_SECRET, data)
    except paytrail.PaytrailException as ex:
        a, b = ex.args
        logger.error('(%s) %s' % (b, a))
        return HttpResponseRedirect(reverse('store:pm:paytrail-failure'))
    except Exception as ex:
        logger.error('%s.' % (ex))
        return HttpResponseRedirect(reverse('store:pm:paytrail-failure'))

    # Save token, redirect
    ta.token = msg['token']
    ta.save()

    # All done, redirect user
    return HttpResponseRedirect(msg['url'])

# Handle failure message from paytrail
def handle_failure(request):
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
        
# Handle success message from paytrail
def handle_success(request):
    return render_to_response('store/success.html')

# Handles the actual success notification from SVM
def handle_notify(request):
    # Get parameters
    order_number = request.GET.get('ORDER_NUMBER', '')
    timestamp = request.GET.get('TIMESTAMP', '')
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
