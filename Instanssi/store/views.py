# -*- coding: utf-8 -*-

from datetime import datetime
from django.contrib.formtools.wizard.views import CookieWizardView
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import render
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from Instanssi.store.forms import StoreProductsForm, StoreInfoForm, StorePaymentMethodForm
from Instanssi.store.methods import paytrail
from Instanssi.store.models import StoreTransaction, TransactionItem

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

        # Save transaction and items
        transaction = info_form.save()
        items_form.save(transaction)

        # Handle payment
        if method_form.cleaned_data['payment_method'] == 0:
            # Handle bitcoin payment
            pass
        else:
            # Handle paytrail payment
            return paytrail.start_process(transaction)


# Index page for store
def index(request):
    return render_to_response('store/index.html', {
    }, context_instance=RequestContext(request))


def has_infodesk_access(request):
    return request.user.is_authenticated() \
        and request.user.is_active \
        and request.user.has_perm('tickets.change_ticket') \
        and request.user.has_perm('store.change_storetransaction')


def mark_item_delivered(request, item_key):
    if not has_infodesk_access(request):
        raise PermissionDenied()

    item = TransactionItem.objects.get(key=item_key)
    item.time_delivered = datetime.now()
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

    if not transaction.is_paid:
        raise Http404

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

    if not ta_item.transaction.is_paid:
        raise Http404

    res = render(request, "store/transaction_item.html", {
        "ta_item": ta_item,
        "has_infodesk_access": has_infodesk_access(request),
    })
    res["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    return res
