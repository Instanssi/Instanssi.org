# -*- coding: utf-8 -*-

from datetime import datetime
import hashlib
import time
import random

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from Instanssi.store.svmlib import svm_request, SVMException, svm_validate, svm_validate_cancelled
from Instanssi.store.forms import StoreOrderForm
from Instanssi.store.models import StoreTransaction, TransactionItem, StoreItem
from Instanssi.tickets.models import Ticket
from Instanssi.store.store_email import ReceiptMailer

# Logging related
import logging
logger = logging.getLogger(__name__)

def gen_sha(text):
    h = hashlib.sha1()
    h.update(text)
    return h.hexdigest()

def terms(request):
    return render_to_response('store/terms.html', {}, context_instance=RequestContext(request))

def privacy(request):
    return render_to_response('store/privacy.html', {}, context_instance=RequestContext(request))

# Index page for store
def index(request):
    # Form domain
    proto = u'http://'
    if settings.SSL_ON:
        proto = u'https://'
    domain = proto + settings.DOMAIN
    
    # Handle request
    if request.method == 'POST':
        transaction_form = StoreOrderForm(request.POST)

        if transaction_form.is_valid():
            ta = transaction_form.save()
            
            # Form data for JSON query
            product_list = []
            for item in TransactionItem.objects.filter(transaction=ta):
                product_list.append({
                    'title': item.item.name,
                    'code': str(item.item.id),
                    'amount': str(item.amount),
                    'price': str(item.item.price),
                    'vat': '0',
                    'type': 1,
                })

            svm_data = {
                'orderNumber': str(ta.id),
                'currency': 'EUR',
                'locale': 'fi_FI',
                'urlSet': {
                    'success': domain + success_url,
                    'failure': domain + failure_url,
                    'notification': domain + reverse('store:notify'),
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
                msg = svm_request(settings.VMAKSUT_ID, settings.VMAKSUT_SECRET, svm_data)
            except SVMException as ex:
                a, b = ex.args
                logger.error('(%s) %s' % (b, a))
                return HttpResponseRedirect(failure_url)
            except Exception as ex:
                logger.error('%s.' % (ex))
                return HttpResponseRedirect(failure_url)

            # Save token, redirect
            ta.time_created = datetime.now()
            ta.token = msg['token']
            ta.save()

            # All done, redirect user
            return HttpResponseRedirect(msg['url'])
    else:
        transaction_form = StoreOrderForm()

    # Check if we have any products to sell
    has_products = False
    if len(StoreItem.items_available()) > 0:
        has_products = True

    # Dump form to index page
    return render_to_response('store/index.html', {
        'transaction_form': transaction_form,
        'has_products': has_products,
    }, context_instance=RequestContext(request))

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
        # Get transaction
        ta = get_object_or_404(StoreTransaction, pk=int(order_number))
        if ta.paid:
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
        # Also, heck if transaction contains tickets
        hastickets = False
        hassnailmail = False
        hasevdelivered = False
        for titem in TransactionItem.objects.filter(transaction=ta):
            mailer.add_item(titem.item.id, titem.item.name, titem.item.price, titem.amount)
            if titem.item.delivery_type == 1:
                hastickets = True
            if titem.item.delivery_type == 2:
                hassnailmail = True
            if titem.item.delivery_type == 3:
                hasevdelivered = True
        
        # Form ticket url
        if hastickets or hasevdelivered:
            proto = 'http://'
            if settings.SSL_ON:
                proto = 'https://'
            ticketurl = proto + settings.DOMAIN + reverse('tickets:tickets', args=(ta.key,))
            mailer.ticketurl(ticketurl)
            
        # Send mail
        try:
            mailer.send()
        except Exception as ex:
            logger.error('%s.' % (ex))
            raise Http404
        
        # Mark as paid
        ta.time_paid = datetime.now()
        ta.status = 1
        if hastickets and not hassnailmail and not hasevdelivered:
            ta.status = 2
        if hastickets and (hassnailmail or hasevdelivered):
            ta.status = 3
        ta.save()
        
        # Generate ticket information for tickets
        for titem in TransactionItem.objects.filter(transaction=ta):
            if titem.item.delivery_type == 1:
                for i in range(titem.amount):
                    ticket = Ticket()
                    ticket.transaction = ta
                    ticket.storeitem = titem.item
                    ticket.event = titem.item.event
                    ticket.owner_firstname = ta.firstname
                    ticket.owner_lastname = ta.lastname
                    ticket.owner_email = ta.email
                    for k in range(10):
                        try:
                            ticket.key = gen_sha('%s|%s|%s|%s|%s|%s|%s' % (i, titem.id, titem.item.id, ta.token, time.time(), random.random(), k))
                            ticket.save()
                            break
                        except IntegrityError as ex:
                            logger.warning("SHA-1 Collision in ticket (WTF!) Key: %s, exception: %s." % (ticket.key, ex))
    else:
        logger.warning("Error while attempting to validate svm notification!")
        raise Http404
        
    # Just respond with something
    return HttpResponse("")


def has_infodesk_access(request):
    return request.user.is_authenticated() \
        and request.user.is_active \
        and request.user.has_perm('tickets.change_ticket') \
        and request.user.has_perm('store.change_storetransaction')


def mark_item_delivered(request, item_key):
    if not has_infodesk_access(request):
        raise PermissionDenied()

    item = TransactionItem.objects.get(key=item_key)
    item.delivered = True
    item.save()


def handle_status_update(request):
    if request.method == 'POST':
        item_key = request.POST.get('ta_item_key')
        if item_key:
            mark_item_delivered(request, item_key)


def ta_view(request, transaction_key):
    """Displays the details of a specific transaction."""

    handle_status_update(request)

    transaction = get_object_or_404(StoreTransaction, key=transaction_key)
    ta_items = TransactionItem.objects.filter(transaction=transaction)

    res = render(request, "store/transaction.html", {
        "transaction": transaction,
        "ta_items": ta_items,
        "has_infodesk_access": has_infodesk_access(request)
    })
    res["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    return res


def ti_view(request, item_key):
    """Displays the details of a specific purchased item."""

    handle_status_update(request)

    ta_item = get_object_or_404(TransactionItem, key=item_key)

    res = render(request, "store/transaction_item.html", {
        "ta_item": ta_item,
        "has_infodesk_access": has_infodesk_access(request),
    })
    res["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    return res
