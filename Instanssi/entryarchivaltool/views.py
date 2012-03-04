# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from Instanssi import settings
from django.http import Http404,HttpResponse
from forms import EntryForm
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from datetime import datetime
from Instanssi.kompomaatti.models import Entry

@login_required
def index(request):
    # Make sure the user is superuser.
    if not request.user.is_superuser:
        raise Http404
    
    # Add form
    saved = False
    if request.method == 'POST':
        addform = EntryForm(request.POST, request.FILES)
        if addform.is_valid():
            # Save form
            addform.save()
            saved = True
            
            # New form for next entry add
            entry = Entry()
            entry.compo = addform.cleaned_data['compo']
            entry.user = addform.cleaned_data['user']
            if addform.cleaned_data['youtube_url']:
                entry.youtube_url = "http://www.youtube.com/v/"
            addform = EntryForm(instance=entry)
    else:
        addform = EntryForm()
    
    # Render response
    return render_to_response("entryarchivaltool/index.html", {
        'addform': addform,
        'saved': saved,
    }, context_instance=RequestContext(request))