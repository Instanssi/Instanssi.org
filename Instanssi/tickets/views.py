# -*- coding: utf-8 -*-

from datetime import datetime
from django.conf import settings
from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from Instanssi.tickets.models import Ticket
from Instanssi.store.models import StoreTransaction

# Logging related
import logging
logger = logging.getLogger(__name__)

# Shows information about a single ticket
def ticket(request, ticket_key):
    # Find ticket
    ticket = get_object_or_404(Ticket, key=ticket_key)
    
    # Render ticket
    return render_to_response('tickets/ticket.html', {
        'ticket': ticket,
    }, context_instance=RequestContext(request))

# Lists all tickets
def tickets(request, transaction_key):
    # Get transaction
    transaction = get_object_or_404(StoreTransaction, key=transaction_key)
    if not transaction.paid:
        raise Http404
    
    # Get all tickets by this transaction
    tickets = Ticket.objects.filter(transaction=transaction)
    
    # Render tickets
    return render_to_response('tickets/tickets.html', {
        'transaction': transaction,
        'tickets': tickets,
    }, context_instance=RequestContext(request))
