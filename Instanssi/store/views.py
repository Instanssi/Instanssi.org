# -*- coding: utf-8 -*-

from datetime import datetime
from django.db import transaction
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from common.responses import JSONResponse
from Instanssi.store.svmlib import svm_request
from Instanssi.store.forms import StoreOrderForm
from Instanssi.store.models import StoreItem, StoreTransaction, TransactionItem

# Logging related
import logging
logger = logging.getLogger(__name__)

# Handles the actual success notification from SVM
def notify_handler(request):
    return JSONResponse({})
