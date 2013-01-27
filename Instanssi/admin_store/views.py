# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.admin_base.misc.auth_decorator import staff_access_required
from Instanssi.store.models import *

# Logging related
import logging
logger = logging.getLogger(__name__)

@staff_access_required
def items(request):
    items = StoreItem.objects.all()

    # Render response
    return admin_render(request, "admin_store/items.html", {
        'items': items,
    })
    
    
@staff_access_required
def status(request):
    transactions = StoreTransaction.objects.all()

    # Render response
    return admin_render(request, "admin_store/status.html", {
        'transactions': transactions,
    })