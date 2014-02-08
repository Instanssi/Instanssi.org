# -*- coding: utf-8 -*-

from datetime import datetime
import hashlib
import time
import random

from django.db import IntegrityError
from django.conf import settings
from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.shortcuts import render

from Instanssi.store.svmlib import svm_validate
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

# Index page for store
def index(request):
    return render_to_response('store/index.html', {}, context_instance=RequestContext(request))

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


def ta_view(request, transaction_key):
    """Displays the details of a specific transaction."""

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

    ta_item = get_object_or_404(TransactionItem, key=item_key)

    res = render(request, "store/transaction_item.html", {
        "ta_item": ta_item,
        "has_infodesk_access": has_infodesk_access(request),
    })
    res["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    return res
