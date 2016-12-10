# -*- coding: utf-8 -*-

from Instanssi.common.http import Http403
from Instanssi.common.auth import staff_access_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.template import loader, Context
from django.forms import inlineformset_factory
from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.store.models import *
from Instanssi.admin_store.forms import StoreItemForm, TaItemExportForm, StoreItemVariantForm

# Logging related
import logging
logger = logging.getLogger(__name__)


@staff_access_required
def index(request):
    return admin_render(request, "admin_store/index.html", {})


@staff_access_required
def export(request):
    if request.method == 'POST':
        form = TaItemExportForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('manage-store:transactions_csv', args=(form.cleaned_data['event'],)))
    else:
        form = TaItemExportForm()
    
    return admin_render(request, "admin_store/export.html", {'form': form})


@staff_access_required
def items(request):
    StoreItemFormSet = inlineformset_factory(
        parent_model=StoreItem, model=StoreItemVariant, form=StoreItemVariantForm, extra=5)

    # Handle form data
    if request.method == 'POST':
        if not request.user.has_perm('store.add_storeitem'):
            raise Http403

        item_form = StoreItemForm(request.POST, request.FILES)
        variant_formset = StoreItemFormSet(request.POST, prefix="nested", instance=item_form.instance)
        if item_form.is_valid() and variant_formset.is_valid():
            item = item_form.save()
            variant_formset.save()
            logger.info('Store Item "{}" added.'.format(item.name), extra={'user': request.user})
            return HttpResponseRedirect(reverse('manage-store:items'))
    else:
        item_form = StoreItemForm()
        variant_formset = StoreItemFormSet(prefix="nested", instance=item_form.instance)

    # Get items
    m_items = StoreItem.objects.all()

    # Render response
    return admin_render(request, "admin_store/items.html", {
        'items': m_items,
        'item_form': item_form,
        'variant_formset': variant_formset
    })


@staff_access_required
def status(request):
    if not request.user.has_perm('store.view_storetransaction'):
        raise Http403
    
    transactions = StoreTransaction.objects.all()

    # Render response
    return admin_render(request, "admin_store/status.html", {
        'transactions': transactions,
    })


@staff_access_required
def tis_csv(request, event_id):
    if not request.user.has_perm('store.view_storetransaction'):
        raise Http403
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="instanssi_store.csv"'
    t = loader.get_template('admin_store/tis_csv.txt')
    c = Context({
        'data': TransactionItem.objects.filter(item__event=event_id),
    })
    response.write(t.render(c))
    return response


@staff_access_required
def tis(request):
    if not request.user.has_perm('store.view_storetransaction'):
        raise Http403
    
    items = TransactionItem.objects.all()

    # Render response
    return admin_render(request, "admin_store/tis.html", {
        'items': items,
    })


@staff_access_required
def transaction_status(request, transaction_id):
    if not request.user.has_perm('store.view_storetransaction'):
        raise Http403
    
    # Get transaction
    transaction = get_object_or_404(StoreTransaction, pk=transaction_id)
    
    # Get items
    items = transaction.get_transaction_items()
    
    # Render response
    return admin_render(request, "admin_store/transactionstatus.html", {
        'transaction_id': int(transaction_id),
        'transaction': transaction,
        'items': items,
    })


@staff_access_required
def edit_item(request, item_id):
    if not request.user.has_perm('store.change_storeitem'):
        raise Http403

    StoreItemFormSet = inlineformset_factory(
        parent_model=StoreItem, model=StoreItemVariant, form=StoreItemVariantForm, extra=3)

    # Get Item
    item = get_object_or_404(StoreItem, pk=item_id)
        
    # Handle form data
    if request.method == 'POST':
        variant_formset = StoreItemFormSet(request.POST, instance=item)
        item_form = StoreItemForm(request.POST, request.FILES, instance=item)
        if item_form.is_valid() and variant_formset.is_valid():
            item_form.save()
            variant_formset.save()
            logger.info('Store Item "{}" edited.'.format(item.name), extra={'user': request.user})
            return HttpResponseRedirect(reverse('manage-store:edit_item', args=(item.id,)))
    else:
        item_form = StoreItemForm(instance=item)
        variant_formset = StoreItemFormSet(instance=item)

    # Render response
    return admin_render(request, "admin_store/itemedit.html", {
        'item_form': item_form,
        'variant_formset': variant_formset
    })
    

@staff_access_required
def delete_item(request, item_id):
    # Check for permissions
    if not request.user.has_perm('store.delete_storeitem'):
        raise Http403
    
    # Delete entry
    try:
        item = StoreItem.objects.get(id=item_id)
        if item.num_sold() == 0:
            item.delete()
            logger.info('Store Item "{}" deleted.'.format(item.name), extra={'user': request.user})
    except StoreItem.DoesNotExist:
        pass
    
    return HttpResponseRedirect(reverse('manage-store:items'))
