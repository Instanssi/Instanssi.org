from allauth.socialaccount.models import SocialAccount
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from Instanssi.common.auth import user_access_required
from Instanssi.users.forms import ProfileForm

AUTH_PROVIDERS = [
    # (provider_id, display_name)
    ("google", "Google"),
    ("github", "Github"),
]


@user_access_required
def profile(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        profileform = ProfileForm(request.POST, instance=request.user, user=request.user)
        if profileform.is_valid():
            profileform.save()
            return HttpResponseRedirect(reverse("users:profile"))
    else:
        profileform = ProfileForm(instance=request.user, user=request.user)

    # Get connected social accounts for this user
    connected = set(SocialAccount.objects.filter(user=request.user).values_list("provider", flat=True))

    # Build provider list: (provider_id, display_name, is_connected)
    providers = [(pid, name, pid in connected) for pid, name in AUTH_PROVIDERS]

    return render(
        request,
        "users/profile.html",
        {"profileform": profileform, "providers": providers},
    )
