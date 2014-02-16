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
from django.contrib.formtools.wizard.views import CookieWizardView

from Instanssi.store.forms import StoreProductsForm, StoreInfoForm, StorePaymentMethodForm
from Instanssi.store.models import StoreTransaction, TransactionItem, StoreItem
from Instanssi.store.methods import paytrail

# Logging related
import logging
logger = logging.getLogger(__name__)

# Terms page
def terms(request):
    """Displays the terms page."""
    return render_to_response('store/terms.html', {}, context_instance=RequestContext(request))

# Privacy info page
def privacy(request):
    """Displays the privacy page"""
    return render_to_response('store/privacy.html', {}, context_instance=RequestContext(request))

class StoreWizard(CookieWizardView):
    """Displays the order form"""
    
    form_list = [StoreProductsForm, StoreInfoForm, StorePaymentMethodForm]
    template_name = 'store/store.html'
    
    def done(self, form_list, **kwargs):
        items_form = form_list[0]
        info_form = form_list[1]
        method_form = form_list[2]
        
        # TODO: Check for errors
        transaction = info_form.save()
        items_form.save(transaction)
        
        # Todo: Change this to real payment method handling
        return render_to_response('store/success.html')
        
# Index page for store
def index(request):
    return render_to_response('store/index.html', {
    }, context_instance=RequestContext(request))

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
