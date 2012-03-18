# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

@login_required(login_url='/control/auth/login/')
def index(request):
    return HttpResponseRedirect("/control/files/")
    