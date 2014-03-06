# -*- coding: utf-8 -*-

from common.http import Http403
from common.auth import staff_access_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.template import loader, Context
from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.store.models import *
from Instanssi.admin_store.forms import StoreItemForm,TaItemExportForm

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
    # Handle form data
    if request.method == 'POST':
        if not request.user.has_perm('store.add_storeitem'):
            raise Http403
        
        form = StoreItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            logger.info('Store Item "'+item.name+'" added.', extra={'user': request.user})
            item.save()
            return HttpResponseRedirect(reverse('manage-store:items'))
    else:
        form = StoreItemForm()

    # Get items
    items = StoreItem.objects.all()

    # Render response
    return admin_render(request, "admin_store/items.html", {
        'items': items,
        'addform': form,
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
    items = transaction.get_items()
    
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
        
    # Get Item
    item = get_object_or_404(StoreItem, pk=item_id)
        
    # Handle form data
    if request.method == 'POST':
        form = StoreItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            logger.info('Store Item "'+item.name+'" edited.', extra={'user': request.user})
            return HttpResponseRedirect(reverse('manage-store:items'))
    else:
        form = StoreItemForm(instance=item)

    # Render response
    return admin_render(request, "admin_store/itemedit.html", {
        'editform': form,
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
            logger.info('Store Item "'+item.name+'" deleted.', extra={'user': request.user})
    except StoreItem.DoesNotExist:
        pass
    
    return HttpResponseRedirect(reverse('manage-store:items'))
