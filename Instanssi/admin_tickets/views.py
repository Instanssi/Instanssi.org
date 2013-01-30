# -*- coding: utf-8 -*-

import hashlib
import time
import random

from common.http import Http403
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db import IntegrityError

from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.admin_base.misc.auth_decorator import staff_access_required
from Instanssi.tickets.models import Ticket
from Instanssi.admin_tickets.forms import TicketForm
from Instanssi.kompomaatti.models import Event

# Logging related
import logging
logger = logging.getLogger(__name__)

# for creating ticket key hash
def gen_sha(text):
    print text
    h = hashlib.sha1()
    h.update(text)
    return h.hexdigest()

@staff_access_required
def index(request, sel_event_id):
    event = get_object_or_404(Event, pk=sel_event_id)
    
    # Handle form data
    if request.method == 'POST':
        if not request.user.has_perm('tickets.add_ticket'):
            raise Http403
        
        # Handle data
        ticketform = TicketForm(request.POST, event=event)
        if ticketform.is_valid():
            ticket = ticketform.save(commit=False)
            ticket.event = event
            for i in range(10):
                try:
                    ticket.key = gen_sha('0|%s|%s|%s|%s' % (event.id, ticket.storeitem.id, random.random(), time.time()))
                    ticket.save()
                except IntegrityError as ex:
                    logger.warning("SHA-1 Collision in admin-ticket (WTF!) Key: %s, exception: %s." % (ticket.key, ex))
                
            logger.info('New ticket created.', extra={'user': request.user, 'event_id': sel_event_id})
            return HttpResponseRedirect(reverse('manage-tickets:index', args=(sel_event_id)))
    else:
        ticketform = TicketForm(event=event)
    
    # Get tickets
    tickets = Ticket.objects.filter(event=sel_event_id)
    
    # Render response
    return admin_render(request, "admin_tickets/index.html", {
        'tickets': tickets,
        'ticketform': ticketform,
        'selected_event_id': int(sel_event_id),
    })
    
@staff_access_required
def edit_ticket(request, sel_event_id, ticket_id):
    if not request.user.has_perm('tickets.change_ticket'):
        raise Http403
    
    # Get event
    event = get_object_or_404(Event, pk=sel_event_id)
    
    # Get ticket
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    
    # Handle form data
    if request.method == 'POST':
        ticketform = TicketForm(request.POST, instance=ticket, event=event)
        if ticketform.is_valid():
            ticketform.save()
            logger.info('Ticket '+ticket.key+' edited.', extra={'user': request.user, 'event_id': sel_event_id})
            return HttpResponseRedirect(reverse('manage-tickets:index', args=(sel_event_id)))
    else:
        ticketform = TicketForm(instance=ticket, event=event)
        
    
    # Render response
    return admin_render(request, "admin_tickets/edit.html", {
        'ticketform': ticketform,
        'selected_event_id': int(sel_event_id),
    })