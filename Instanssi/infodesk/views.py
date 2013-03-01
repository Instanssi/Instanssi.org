# -*- coding: utf-8 -*-

from common.responses import JSONResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from Instanssi.infodesk.misc.auth_decorator import infodesk_access_required
from Instanssi.infodesk.forms import TransactionKeyScanForm, TicketKeyScanForm
from Instanssi.tickets.models import Ticket
from Instanssi.store.models import StoreTransaction, TransactionItem
from Instanssi.kompomaatti.models import Event

# Logging related
import logging
logger = logging.getLogger(__name__)


@infodesk_access_required
def index(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    return render_to_response('infodesk/index.html', {
        'event': event
    }, context_instance=RequestContext(request))


@infodesk_access_required
def ticket_lookup_autocomplete(request, event_id):
    lookup = request.GET['term']

    # lookup name in people who have bought something
    txns = StoreTransaction.objects.filter(lastname__istartswith=lookup)
    return JSONResponse(['%s, %s' % (t.lastname, t.firstname) for t in txns])


@infodesk_access_required
def ticket_lookup(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    # The form autocompletes names like "lastname, firstname"
    # If somebody wrote a comma in their name, they can buy a new ticket.
    # We could also accept ids (with some potential UI problems).
    firstname = None
    lastname = None

    try:
        names = request.GET['name']
        name = names.split(',')
        lastname = name[0]
        firstname = name[1].lstrip()
    except:
        pass

    storetransactions = StoreTransaction.objects.filter(
        lastname=lastname,
        firstname=firstname
    )

    transactions = []
    for transaction in storetransactions:
        transactions.append({
            'id': transaction.id,
            'created': transaction.time_created,
            'status': transaction.get_status_display,
            'tickets': Ticket.objects.filter(transaction=transaction),
            'others': TransactionItem.objects.filter(
                transaction=transaction).exclude(item__delivery_type=1)
        })

    return render_to_response('infodesk/ticket_lookup.html', {
        'Ticket': Ticket,
        'event': event,
        'transactions': transactions,
        'name': names
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
    logger.info('Ticket %d marked as used.' % (ticket.id,), extra={'user': request.user, 'event_id': event_id})
    return HttpResponseRedirect(reverse('infodesk:index', args=(event_id,)))


@infodesk_access_required
def store_mark(request, event_id, transaction_id):
    ta = get_object_or_404(StoreTransaction, pk=transaction_id)
    ta.status = 2
    ta.save()
    logger.info('Transaction %d marked as delivered.' % (ta.id,), extra={'user': request.user, 'event_id': event_id})
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
