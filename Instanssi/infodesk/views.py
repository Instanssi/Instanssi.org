# -*- coding: utf-8 -*-

from common.http import Http403
from common.responses import JSONResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from Instanssi.infodesk.misc.auth_decorator import infodesk_access_required
from Instanssi.infodesk.forms import TransactionKeyScanForm, TicketKeyScanForm
from Instanssi.tickets.models import Ticket
from Instanssi.store.models import StoreTransaction
from Instanssi.kompomaatti.models import Event
    
@infodesk_access_required
def index(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    return render_to_response('infodesk/index.html', {
        'event': event
    }, context_instance=RequestContext(request))

@infodesk_access_required
def ticket_check(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    
    if request.method == 'POST':
        form = TicketKeyScanForm(request.POST, event=event)
        if form.is_valid():
            return HttpResponseRedirect(reverse('infodesk:ticket_info', args=(event.id, form.ticket.id,)))
    else:
        form = TicketKeyScanForm(event=event)
    
    return render_to_response('infodesk/ticket_check.html', {
        'event': event, 
        'form': form
    }, context_instance=RequestContext(request))

@infodesk_access_required
def store_check(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    
    if request.method == 'POST':
        form = TransactionKeyScanForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('infodesk:store_info', args=(event.id, form.transaction.id,)))
    else:
        form = TransactionKeyScanForm()
    
    return render_to_response('infodesk/store_check.html', {
        'event': event, 
        'form': form
    }, context_instance=RequestContext(request))

@infodesk_access_required
def ticket_mark(request, event_id, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    ticket.used = True
    ticket.save()
    return HttpResponseRedirect(reverse('infodesk:index', args=(event_id,)))

@infodesk_access_required
def store_mark(request, event_id, transaction_id):
    ta = get_object_or_404(StoreTransaction, pk=transaction_id)
    ta.status = 2
    ta.save()
    return HttpResponseRedirect(reverse('infodesk:index', args=(event_id,)))

@infodesk_access_required
def ticket_info(request, event_id, ticket_id):
    event = get_object_or_404(Event, pk=event_id)
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    return render_to_response('infodesk/ticket_info.html', {
        'event': event, 
        'ticket': ticket
    }, context_instance=RequestContext(request))

@infodesk_access_required
def store_info(request, event_id, transaction_id):
    event = get_object_or_404(Event, pk=event_id)
    transaction = get_object_or_404(StoreTransaction, pk=transaction_id)
    return render_to_response('infodesk/store_info.html', {
        'event': event, 
        'transaction': transaction
    }, context_instance=RequestContext(request))
