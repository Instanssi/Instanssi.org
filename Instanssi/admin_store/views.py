# -*- coding: utf-8 -*-

from common.http import Http403
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.admin_base.misc.auth_decorator import staff_access_required
from Instanssi.store.models import *
from Instanssi.admin_store.forms import StoreItemForm, StoreItemEditForm

# Logging related
import logging
logger = logging.getLogger(__name__)

@staff_access_required
def items(request):
    # Handle form data
    if request.method == 'POST':
        if not request.user.has_perm('store.add_storeitem'):
            raise Http403
        
        form = StoreItemForm(request.POST)
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
    transactions = StoreTransaction.objects.all()

    # Render response
    return admin_render(request, "admin_store/status.html", {
        'transactions': transactions,
    })
    
@staff_access_required
def transaction_status(request, transaction_id):
    # Render response
    return admin_render(request, "admin_store/transactionstatus.html", {
        'transaction_id': int(transaction_id),
    })
    
@staff_access_required
def edit_item(request, item_id):
    if not request.user.has_perm('store.change_storeitem'):
        raise Http403
        
    # Get Item
    item = get_object_or_404(StoreItem, pk=item_id)
        
    # Handle form data
    if request.method == 'POST':
        form = StoreItemEditForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            logger.info('Store Item "'+item.name+'" edited.', extra={'user': request.user})
            return HttpResponseRedirect(reverse('manage-store:items'))
    else:
        form = StoreItemEditForm(instance=item)

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
        item.delete()
        logger.info('Store Item "'+item.name+'" deleted.', extra={'user': request.user})
    except StoreItem.DoesNotExist:
        pass
    
    return HttpResponseRedirect(reverse('manage-store:items'))
