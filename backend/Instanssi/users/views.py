from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from Instanssi.common.auth import user_access_required
from Instanssi.users.forms import ProfileForm


def loggedout(request: HttpRequest) -> HttpResponse:
    return render(request, "users/loggedout.html")


@user_access_required
def profile(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        profileform = ProfileForm(request.POST, instance=request.user, user=request.user)
        if profileform.is_valid():
            profileform.save()
            return HttpResponseRedirect(reverse("users:profile"))
    else:
        profileform = ProfileForm(instance=request.user, user=request.user)

    return render(
        request,
        "users/profile.html",
        {"profileform": profileform},
    )
