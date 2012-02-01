# -*- coding: utf-8 -*-

from django.db import IntegrityError
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime

from Instanssi.kompomaatti.misc.custom_render import custom_render
from Instanssi.kompomaatti.misc.time_formatting import compo_times_formatter
from Instanssi.kompomaatti.models import Compo, Entry, Vote, VoteCode, VoteCodeRequest
from Instanssi.kompomaatti.forms import EntryForm, VoteCodeAssocForm, RequestVoteCodeForm

@login_required
def dashboard(request): 
    # Get list of users entries
    my_entries = Entry.objects.filter(user=request.user)
    
    # Get list of open compos, format times
    open_compos = Compo.objects.filter(active=True, adding_end__gte = datetime.now())
    oclist = []
    for compo in open_compos:
        formatted_compo = compo_times_formatter(compo)
        oclist.append(formatted_compo)

    # Check if we got data from vote code assoc form
    if request.method == 'POST' and request.POST['formtype'] == 'votecodeassocform':
        assocform = VoteCodeAssocForm(request.POST)
        if assocform.is_valid():
            code = assocform.cleaned_data['code']
            try:
                vc = VoteCode.objects.get(key=code)
                vc.associated_to = request.user
                vc.time = datetime.now()
                vc.save()
            except VoteCode.DoesNotExist:
                pass
            return HttpResponseRedirect('/kompomaatti/myentries/') 
    else:
        assocform = VoteCodeAssocForm()
    
    # Get last VoteCodeRequest, if it exists
    try:
        vcreq = VoteCodeRequest.objects.get(user=request.user)
    except VoteCodeRequest.DoesNotExist:
        vcreq = None
    
    # Check if we got data from vote code request form
    if request.method == 'POST' and request.POST['formtype'] == 'requestvotecodeform':
        requestform = RequestVoteCodeForm(request.POST)
        if requestform.is_valid():
            if vcreq:
                vcreq.text = requestform.cleaned_data['text']
                vcreq.save()
            else:
                req = requestform.save(commit=False)
                req.user = request.user
                req.save()
            return HttpResponseRedirect('/kompomaatti/myentries/') 
    else:
        if vcreq:
            requestform = RequestVoteCodeForm(instance=vcreq)
        else:
            requestform = RequestVoteCodeForm()
        
    # Dump the page to the user
    return custom_render(request, 'kompomaatti/myentries.html', {
        'myentries': my_entries,
        'opencompos': oclist,
        'user': request.user,
        'assocform': assocform,
        'requestform': requestform,
    })

@login_required
def delentry(request, entry_id):
    # Check if entry exists and get the object
    try:
        entry = Entry.objects.get(id=entry_id)
    except ObjectDoesNotExist:
        raise Http404

    # Make sure the user owns the entry
    if entry.user != request.user:
        raise Http404    

    # Make sure the compo is active and if adding time is open
    if not entry.compo.active or entry.compo.editing_end < datetime.now():
        raise Http404
    
    # Delete entry and associated files
    if entry.entryfile:
        entry.entryfile.delete()
    if entry.sourcefile:
        entry.sourcefile.delete()
    if entry.imagefile_original:
        entry.imagefile_original.delete()
    entry.delete()
    
    # Redirect back to dashboard
    return HttpResponseRedirect('/kompomaatti/myentries/') 

@login_required
def addentry(request, compo_id):
    # Check if entry exists and get the object
    try:
        compo = Compo.objects.get(id=compo_id)
    except ObjectDoesNotExist:
        raise Http404
    
    # Make sure the compo is active and if adding time is open
    if not compo.active or compo.adding_end < datetime.now():
        raise Http404
    
    # Check if we got filled form
    if request.method == 'POST':
        addform = EntryForm(request.POST, request.FILES, compo=compo, legend="Uusi tuotos")
        if addform.is_valid():
            nentry = addform.save(commit=False)
            nentry.user = request.user
            nentry.compo = compo
            nentry.save()
            return HttpResponseRedirect('/kompomaatti/myentries/') 
    else:
        addform = EntryForm(compo=compo, legend="Uusi tuotos")

    # Return the edit form
    return custom_render(request, 'kompomaatti/addentry.html', {
        'addform': addform,
        'compo': compo,
    })

@login_required
def editentry(request, entry_id):
    # Check if entry exists and get the object
    try:
        entry = Entry.objects.get(id=entry_id)
    except ObjectDoesNotExist:
        raise Http404
    
    # Make sure the user owns the entry
    if entry.user != request.user:
        raise Http404
    
    # Make sure the compo is active and if adding time is open
    if not entry.compo.active or entry.compo.editing_end < datetime.now():
        raise Http404
    
    # Check if we got filled form    
    if request.method == 'POST':
        editform = EntryForm(request.POST, request.FILES, instance=entry, editing=True, compo=entry.compo, legend="Muokkaa tuotosta")
        if editform.is_valid():
            editform.save()
            return HttpResponseRedirect('/kompomaatti/myentries/') 
    else:
        editform = EntryForm(instance=entry, editing=True, compo=entry.compo, legend="Muokkaa tuotosta")
    
    # Return the edit form
    return custom_render(request, 'kompomaatti/editentry.html', {
        'editform': editform,
        'entry': entry,
    })