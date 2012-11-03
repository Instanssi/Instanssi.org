# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import Http404,HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from forms import LoginForm
from Instanssi.admin_base.misc.auth_decorator import staff_access_required

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
                    return HttpResponseRedirect("/manage/")
                
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

@staff_access_required
def logout_action(request):
    logout(request)
    return HttpResponseRedirect("/manage/auth/loggedout/")