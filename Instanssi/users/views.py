# -*- coding: utf-8 -*-

from Instanssi.common.auth import user_access_required
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.core.urlresolvers import reverse
from Instanssi.users.forms import OpenIDLoginForm, DjangoLoginForm, ProfileForm
from Instanssi.common.misc import get_url_local_path


AUTH_METHODS = [
    # Short name, social-auth, friendly name
    ('facebook', 'facebook', 'Facebook'),
    ('google', 'google-oauth2', 'Google'),
    ('twitter', 'twitter', 'Twitter'),
    ('github', 'github', 'Github'),
    ('battlenet', 'battlenet-oauth2', 'Battle.net'),
    ('steam', 'steam', 'Steam'),
]


def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('users:profile'))
    
    # Get referer for redirect
    # Make sure that the referrer is a local path.
    if 'next' in request.GET:
        next_page = get_url_local_path(request.GET['next'])
    else:
        next_page = get_url_local_path(request.META.get('HTTP_REFERER', reverse('users:profile')))

    # Test django login form
    if request.method == "POST":
        djangoform = DjangoLoginForm(request.POST)
        if djangoform.is_valid():
            djangoform.login(request)
            return HttpResponseRedirect(djangoform.cleaned_data['next'])
    else:
        djangoform = DjangoLoginForm(next=next_page)
    
    # Openid login form
    # The form will be handled elsewhere; this is only for rendering the form.
    openidform = OpenIDLoginForm(next=next_page)
    
    # Render response
    return render(request, "users/login.html", {
        'djangoform': djangoform,
        'openidform': openidform,
        'next': next_page,
        'AUTH_METHODS': AUTH_METHODS
    })


def loggedout(request):
    return render(request, "users/loggedout.html")


@user_access_required
def profile(request):
    from social_django.models import DjangoStorage

    if request.method == "POST":
        profileform = ProfileForm(request.POST, instance=request.user, user=request.user)
        if profileform.is_valid():
            profileform.save()
            return HttpResponseRedirect(reverse('users:profile'))
    else:
        profileform = ProfileForm(instance=request.user, user=request.user)

    # Get all active providers for this user
    active_providers = []
    for social_auth in DjangoStorage.user.get_social_auth_for_user(request.user):
        active_providers.append(social_auth.provider)

    # Providers list
    methods = []
    for method in AUTH_METHODS:
        methods.append(method + (method[1] in active_providers, ))

    return render(request, "users/profile.html", {
        'profileform': profileform,
        'active_providers': active_providers,
        'AUTH_METHODS': methods
    })


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('users:loggedout'))
