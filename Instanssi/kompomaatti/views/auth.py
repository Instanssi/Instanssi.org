# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponseRedirect

@login_required
def dologout(request):
    logout(request)
    return HttpResponseRedirect('/kompomaatti/') 