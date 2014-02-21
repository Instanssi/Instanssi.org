# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import Http404,HttpResponseRedirect
from django.contrib import auth
from django.template import RequestContext
from django.core.urlresolvers import reverse
from Instanssi.users.forms import OpenIDLoginForm, DjangoLoginForm, ProfileForm
from Instanssi.users.misc.auth_decorator import user_access_required

def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('users:profile'))
    
    error = False
    if request.method == "POST":
        djangoform = DjangoLoginForm(request.POST)
        if djangoform.is_valid():
            username = djangoform.cleaned_data['username']
            password = djangoform.cleaned_data['password']
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    return HttpResponseRedirect(reverse('users:profile'))
            error = True
    else:
        djangoform = DjangoLoginForm()
    
    openidform = OpenIDLoginForm(next=reverse('users:profile'))
    
    # Render response
    return render_to_response("users/login.html", {
        'djangoform': djangoform,
        'openidform': openidform,
        'error': error,
    }, context_instance=RequestContext(request))

def loggedout(request):
    return render_to_response("users/loggedout.html")

@user_access_required
def profile(request):
    if request.method == "POST":
        profileform = ProfileForm(request.POST, instance=request.user, user=request.user)
        if profileform.is_valid():
            profileform.save()
            return HttpResponseRedirect(reverse('users:profile'))
    else:
        profileform = ProfileForm(instance=request.user, user=request.user)
    
    return render_to_response("users/profile.html", {
        'profileform': profileform,
    }, context_instance=RequestContext(request))

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('users:loggedout'))
