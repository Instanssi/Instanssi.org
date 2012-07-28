# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import Http404,HttpResponseRedirect,HttpResponse
from django.contrib.auth.decorators import login_required
from Instanssi.dbsettings.models import Setting
from Instanssi.kompomaatti.models import Compo,Entry,VoteCodeRequest,VoteCode,Event
from Instanssi.admin_kompomaatti.forms import AdminCompoForm, AdminEntryForm, AdminEntryAddForm, CreateTokensForm
from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.admin_base.misc.eventsel import get_selected_event
from Instanssi.kompomaatti.misc import entrysort

# For votecode stuff
from django.db import IntegrityError
from datetime import datetime
import random
import hashlib
    
# For generating a paper version of votecodes
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
    
    
@login_required(login_url='/control/auth/login/')
def compo_browse(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Get compos
    selected_event_id = get_selected_event(request)
    compos = Compo.objects.filter(event=selected_event_id)
    
    # Form handling
    if request.method == "POST":
        compoform = AdminCompoForm(request.POST)
        if compoform.is_valid():
            data = compoform.save(commit=False)
            data.event_id = active_event_id
            data.save()
            return HttpResponseRedirect('/control/kompomaatti/compos/') 
    else:
        compoform = AdminCompoForm()
    
    # Render response
    return admin_render(request, "admin_kompomaatti/compo_browse.html", {
        'compos': compos,
        'compoform': compoform,
    })
    
@login_required(login_url='/control/auth/login/')
def compo_add(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Get compos
    selected_event_id = get_selected_event(request)
    
    # Form handling
    if request.method == "POST":
        compoform = AdminCompoForm(request.POST)
        if compoform.is_valid():
            data = compoform.save(commit=False)
            data.event_id = selected_event_id
            data.save()
            return HttpResponseRedirect('/control/kompomaatti/compos/') 
    else:
        compoform = AdminCompoForm()
    
    # Render response
    return admin_render(request, "admin_kompomaatti/compo_add.html", {
        'compoform': compoform,
    })
    
@login_required(login_url='/control/auth/login/')
def compo_edit(request, compo_id):
    # Make sure the user is staff.index.html
    if not request.user.is_staff:
        raise Http404
    
    # Check ID
    try:
        compo = Compo.objects.get(id=compo_id)
    except:
        raise Http404
    
    # Handle form
    if request.method == "POST":
        editform = AdminCompoForm(request.POST, instance=compo)
        if editform.is_valid():
            editform.save()
            return HttpResponseRedirect('/control/kompomaatti/entries/') 
    else:
        editform = AdminCompoForm(instance=compo)
    
    # Render response
    return admin_render(request, "admin_kompomaatti/compo_edit.html", {
        'compo': compo,
        'editform': editform,
    })
    
@login_required(login_url='/control/auth/login/')
def entry_browse(request):
    # Make sure the user is staff.index.html
    if not request.user.is_staff:
        raise Http404
    
    # Get Entries    
    selected_event_id = get_selected_event(request)
    compos = Compo.objects.filter(event=selected_event_id)
    entries = Entry.objects.filter(compo__in=compos)
    
    # Render response
    return admin_render(request, "admin_kompomaatti/entry_browse.html", {
        'entries': entries,
    })
    
@login_required(login_url='/control/auth/login/')
def entry_edit(request, entry_id):
    # Make sure the user is staff.index.html
    if not request.user.is_staff:
        raise Http404
    
    # Check ID
    try:
        entry = Entry.objects.get(id=entry_id)
    except:
        raise Http404
    
    # Handle form
    if request.method == "POST":
        editform = AdminEntryForm(request.POST, request.FILES, instance=entry)
        if editform.is_valid():
            editform.save()
            return HttpResponseRedirect('/control/kompomaatti/entries/') 
    else:
        editform = AdminEntryForm(instance=entry)
    
    # Render response
    return admin_render(request, "admin_kompomaatti/entry_edit.html", {
        'entry': entry,
        'editform': editform,
    })
    
@login_required(login_url='/control/auth/login/')
def entry_add(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Get compos
    selected_event_id = get_selected_event(request)
    
    # Form handling
    if request.method == "POST":
        entryform = AdminEntryAddForm(request.POST, request.FILES)
        if entryform.is_valid():
            data = entryform.save(commit=False)
            data.event_id = selected_event_id
            data.save()
            return HttpResponseRedirect('/control/kompomaatti/entries/') 
    else:
        entryform = AdminEntryAddForm()
    
    # Render response
    return admin_render(request, "admin_kompomaatti/entry_add.html", {
        'entryform': entryform,
    })
    
@login_required(login_url='/control/auth/login/')
def results(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Get compos
    selected_event_id = get_selected_event(request)
    try:
        compos = Compo.objects.filter(event_id=selected_event_id)
    except Entry.DoesNotExist:
        raise Http404
    
    # Get the entries
    results = {}
    for compo in compos:
        results[compo.name] = entrysort.sort_by_score(Entry.objects.filter(compo=compo))
    
    # Render response
    return admin_render(request, "admin_kompomaatti/results.html", {
        'results': results,
    })
    
@login_required(login_url='/control/auth/login/')
def votecodes(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
        
    # Get tokens
    selected_event_id = get_selected_event(request)
    tokens = VoteCode.objects.filter(event_id=selected_event_id)
    
    # Render response
    return admin_render(request, "admin_kompomaatti/votecodes.html", {
        'tokens': tokens,
    })
    
@login_required(login_url='/control/auth/login/')
def votecodes_print(request):
    # Make sure the user is superuser.
    if not request.user.is_staff:
        raise Http404
    
    # Get free votecodes
    selected_event_id = get_selected_event(request)
    codes = VoteCode.objects.filter(event_id=selected_event_id, associated_to=None)
    
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=votecodes.pdf'

    # Create the PDF object,
    p = canvas.Canvas(response)
    p.setAuthor(u"Kompomaatti")
    p.setTitle(u"Äänestyskoodeja")
    p.setFont("Helvetica-Oblique", 18)

    # Print codes
    height = 0
    step = 2.12*cm
    perpage = 14
    codeno = 0
    for code in codes:
        p.line(0,height,21*cm,height)
        p.drawString(1*cm, height+0.8*cm, u"Äänestyskoodi: "+code.key)
        height += step
        codeno += 1
        if codeno >= perpage:
            p.showPage()
            p.setFont("Helvetica-Oblique", 18)
            height = 0
            codeno = 0
    p.showPage()

    # Close the PDF object & dump out the response
    p.save()
    return response
    
@login_required(login_url='/control/auth/login/')
def votecodes_generate(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Get active event id
    try:
        selected_event_id = get_selected_event(request)
        event = Event.objects.get(id=selected_event_id)
    except:
        event = None

    # Handle form
    gentokensform = None
    if event != None:
        # Check if we got filled form
        if request.method == 'POST':
            gentokensform = CreateTokensForm(request.POST)
            if gentokensform.is_valid():
                amount = int(gentokensform.cleaned_data['amount'])
                for n in range(amount):
                    try:
                        c = VoteCode()
                        c.event = event
                        c.key = unicode(hashlib.md5(str(random.random())).hexdigest()[:8])
                        c.save()
                    except IntegrityError:
                        n = n-1 # Ugly, may cause infinite loop...
                return HttpResponseRedirect('/control/kompomaatti/votecodes/') 
        else:
            gentokensform = CreateTokensForm()
        
    # Render response
    return admin_render(request, "admin_kompomaatti/votecodes_add.html", {
        'gentokensform': gentokensform,
    })
    
@login_required(login_url='/control/auth/login/')
def votecoderequests(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Get all requests
    requests = VoteCodeRequest.objects.all()
    
    # Render response
    return admin_render(request, "admin_kompomaatti/vcrequests.html", {
        'requests': requests,
    })
    
@login_required
def votecoderequests_accept(request, vcrid):
    # Make sure the user is superuser.
    if not request.user.is_superuser:
        raise Http404
    
    # Get the request
    try:
        vcr = VoteCodeRequest.objects.get(id=vcrid)
    except VoteCodeRequest.DoesNotExist:
        raise Http404
        
    # Get active event
    event = None
    try:
        event = Event.objects.get(id=get_selected_event(request))
    except:
        raise Http404
        
    # Add votecode for user. Bang your head to the wall until you succeed, etc.
    # Really, do something about this later!
    # TODO: Do something about this shit!
    done = False
    for i in range(25):
        try:
            c = VoteCode()
            c.event = event
            c.key = unicode(hashlib.md5(str(random.random())).hexdigest()[:8])
            c.associated_to = vcr.user
            c.time = datetime.now()
            c.save()
            done = True
            break;
        except IntegrityError:
            pass
    
    if not done:
        return HttpResponse("Virhe yritettäessä lisätä satunnaista avainta ... FIXME!")
            
    # Delete request
    vcr.delete()
    
    # Return to admin page
    return HttpResponseRedirect('/control/kompomaatti/votecoderequests/') 
