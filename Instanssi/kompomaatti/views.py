# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from models import Compo, Entry, Vote
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseRedirect, HttpResponse
from forms import AddEntryForm
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from datetime import datetime
from Instanssi.kompomaatti.misc import awesometime

def custom_render(request, tpl, context={}):
    compos = Compo.objects.all()
    context['compos'] = compos
    context['logged'] = request.user.is_authenticated()
    return render_to_response(tpl, context, context_instance=RequestContext(request))


def index(request):
    return custom_render(request, 'kompomaatti/index.html')


def help(request):
    return custom_render(request, 'kompomaatti/help.html')

@login_required
def myprods(request): 
    # Handle adding an antry
    if request.method == 'POST':
        addform = AddEntryForm(request.POST, request.FILES) 
        if addform.is_valid(): 
            nentry = addform.save(commit=False)
            nentry.user = request.user
            nentry.save()
            return HttpResponseRedirect('/kompomaatti/myprods/') 
    else:
        addform = AddEntryForm() 

    # Get list of users entries
    my_entries = Entry.objects.filter(user=request.user)

    # Dump the page to the user
    return custom_render(request, 'kompomaatti/myprods.html', {
        'addform': addform,
        'myentries': my_entries
    })


def compo_times_formatter(compo):
    compo.compo_time = awesometime.format_single(compo.compo_start)
    compo.adding_time = awesometime.format_single(compo.adding_end)
    compo.editing_time = awesometime.format_single(compo.editing_end)
    compo.voting_time = awesometime.format_between(compo.voting_start, compo.voting_end)
    return compo

def compo(request, compo_id):
    # Get compo information
    try:
        c = Compo.objects.get(id=compo_id, active=True)
    except ObjectDoesNotExist:
        raise Http404
    
    # Format times and stuff
    c = compo_times_formatter(c)
    
    # The following is only relevant, if the user is logged in and valid.
    has_voted = False
    voting_open = False
    if request.user.is_authenticated():
        # Check if user has already voted
        votes = Vote.objects.filter(user=request.user, compo=c).order_by('rank')
        if votes.count() > 0:
            has_voted = True
        
        # Check if voting is open
        now = datetime.now()
        if c.voting_start <= now and now < c.voting_end:
            voting_open = True
    
        # Check if we want to do something with forms and stuff.
        if request.method == 'POST':
            if voting_open:
                # Remove old votes by this user, on this compo
                if has_voted:
                    Vote.objects.filter(user=request.user, compo=c).delete()
                
                # List of all ranks in order
                order_raw = request.POST.getlist('order[]')
                order = []
                for id in order_raw:
                    order.append(int(id))
                
                # Check voting input for cheating :P
                # See if all entries have a rank.
                for entry in Entry.objects.filter(compo=c):
                    if entry.id not in order:
                        return HttpResponse("1")
                    
                # Add new votes, if there were no errors
                number = 1
                for entry_id in order:
                    vote = Vote()
                    vote.user = request.user
                    vote.compo = c
                    vote.entry = Entry.objects.get(id=entry_id)
                    vote.rank = number
                    vote.save()
                    number += 1
                        
                return HttpResponse("0")
            else:
                raise Http404
    
    # Get entries.
    # If voting is open, and user has already voted, get the order of entries by previous voting
    # If voting is open, and user has NOT voted yet, get the entries in random order
    # Otherwise just get entries and sort by name
    if voting_open and has_voted:
        e = []
        for vote in votes:
            e.append(vote.entry)
    elif voting_open:
        e = Entry.objects.filter(compo=c).order_by('?')
    else:
        e = Entry.objects.filter(compo=c).order_by('name')
    
    # Render the page. Ya, rly.
    return custom_render(request, 'kompomaatti/compo.html', {
        'compo': c,
        'entries': e,
        'voting_open': voting_open,
        'has_voted': has_voted
    })


def compolist(request):
    # Get compos, format times
    composet = Compo.objects.filter(active=True).order_by('compo_start')
    compos = []
    for compo in composet:
        compos.append(compo_times_formatter(compo))
    
    # Get entries in compos
    # TODO: Get order by voting results
    entries = {}
    for compo in compos:
        entries[compo.id] = Entry.objects.filter(compo=compo)

    # Return page
    return custom_render(request, 'kompomaatti/compolist.html', {
        'compolist': compos,
        'entries': entries,
    })


def entry(request, entry_id):
    # Get the entry. Show 404 if it doesn't exist ...
    try:
        entry = Entry.objects.get(id=entry_id)
    except ObjectDoesNotExist:
        raise Http404
    
    return custom_render(request, 'kompomaatti/entry.html', {
        'entry': entry
    })

def dologout(request):
    logout(request)
    return HttpResponseRedirect('/kompomaatti/') 
