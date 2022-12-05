import logging

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from oauth2_provider.models import Application

from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.admin_users.forms import (
    ApiApplicationForm,
    UserCreationForm,
    UserEditForm,
)
from Instanssi.common.auth import staff_access_required, su_access_required
from Instanssi.dblog.models import DBLogEntry

logger = logging.getLogger(__name__)


@staff_access_required
def index(request: HttpRequest) -> HttpResponse:
    return admin_render(request, "admin_users/index.html", {})


@staff_access_required
def log(request: HttpRequest) -> HttpResponse:
    return admin_render(
        request, "admin_users/log.html", {"entries": DBLogEntry.objects.all().order_by("-date")}
    )


@staff_access_required
def users(request: HttpRequest) -> HttpResponse:
    if request.user.is_superuser:
        if request.method == "POST":
            user_form = UserCreationForm(request.POST)
            if user_form.is_valid():
                user_form.save()
                logger.info("User added.", extra={"user": request.user})
                return HttpResponseRedirect(reverse("manage-users:index"))
        else:
            user_form = UserCreationForm()
    else:
        user_form = None

    return admin_render(
        request,
        "admin_users/users.html",
        {
            "superusers": User.objects.exclude(username="arkisto"),
            "userform": user_form,
        },
    )


@staff_access_required
def apps(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        add_form = ApiApplicationForm(request.POST, user=request.user)
        if add_form.is_valid():
            app = add_form.save()
            logger.info("Application %s created.", app.name, extra={"user": request.user})
            return HttpResponseRedirect(reverse("manage-users:apps"))
    else:
        add_form = ApiApplicationForm()

    m_apps = Application.objects.filter(user=request.user)
    all_apps = Application.objects.all() if request.user.is_superuser else None
    return admin_render(
        request,
        "admin_users/api_tokens.html",
        {"apps": m_apps, "add_form": add_form, "all_apps": all_apps},
    )


@staff_access_required
def delete_app(request: HttpRequest, app_id: int) -> HttpResponse:
    try:
        q = Application.objects.get_queryset()
        if not request.user.is_superuser:
            q = q.filter(user=request.user)
        app = q.get(id=app_id)
    except Application.DoesNotExist:
        raise Http404

    logger.info("Application %s deleted.", app.name, extra={"user": request.user})
    app.delete()
    return HttpResponseRedirect(reverse("manage-users:apps"))


@su_access_required
def edit(request: HttpRequest, su_id: int) -> HttpResponse:
    # Get user info and make sure it's not SU we're trying to edit
    user = get_object_or_404(User, pk=su_id)
    if user.is_superuser:
        raise PermissionDenied()

    if request.method == "POST":
        user_form = UserEditForm(request.POST, instance=user)
        if user_form.is_valid():
            user_form.save()
            logger.info('User "{}" edited.'.format(user.username), extra={"user": request.user})
            return HttpResponseRedirect(reverse("manage-users:index"))
    else:
        user_form = UserEditForm(instance=user)

    return admin_render(request, "admin_users/edit.html", {"userform": user_form})


@su_access_required
def delete(request: HttpRequest, su_id: int) -> HttpResponse:
    user = get_object_or_404(User, pk=su_id)
    if user.is_superuser or user.username == "arkisto":
        raise PermissionDenied()

    logger.info("User '%s' deactivated.", user.username, extra={"user": request.user})
    user.is_active = False
    user.save()
    return HttpResponseRedirect(reverse("manage-users:users"))
