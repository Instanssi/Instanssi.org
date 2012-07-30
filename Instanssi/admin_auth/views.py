# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import Http404,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from forms import LoginForm

def login_action(request):
    error = False
    if request.method == "POST":
        loginform = LoginForm(request.POST)
        if loginform.is_valid():
            username = loginform.cleaned_data['username']
            password = loginform.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active and user.is_staff:
                    login(request, user)
                    return HttpResponseRedirect("/control/")
                
            # If everything fails, raise error flag
            error = True
    else:
        loginform = LoginForm()
    
    # Render response
    return render_to_response("admin_auth/login.html", {
        'loginform': loginform,
        'error': error,
    }, context_instance=RequestContext(request))

def logout_page(request):
    return render_to_response("admin_auth/loggedout.html")

@login_required(login_url='/control/auth/login/')
def logout_action(request):
    logout(request)
    return HttpResponseRedirect("/control/auth/loggedout/")