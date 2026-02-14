from __future__ import annotations

from typing import Any

from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Fieldset, Layout, Submit
from django import forms
from django.contrib import auth
from django.core.exceptions import ValidationError
from django.http import HttpRequest

from Instanssi.common.misc import get_url_local_path
from Instanssi.kompomaatti.models import Profile
from Instanssi.users.models import User


class DjangoLoginForm(forms.Form):
    username = forms.CharField(label="Käyttäjätunnus")
    password = forms.CharField(label="Salasana", widget=forms.PasswordInput)
    next = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.next_page: str = kwargs.pop("next", "")
        self.logged_user: User | None = None
        super(DjangoLoginForm, self).__init__(*args, **kwargs)
        self.fields["next"].initial = self.next_page
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Kirjautuminen käyttäjätunnuksilla",
                "username",
                "password",
                "next",
                ButtonHolder(Submit("submit", "Kirjaudu")),
            )
        )

    def clean_next(self) -> str:
        return get_url_local_path(self.cleaned_data["next"])

    def clean(self) -> dict[str, Any] | None:
        # Make sure the user is valid
        cleaned_data = super(DjangoLoginForm, self).clean()

        if "username" in self.cleaned_data and "password" in self.cleaned_data:
            self.logged_user = auth.authenticate(
                username=self.cleaned_data["username"], password=self.cleaned_data["password"]
            )
            if not self.logged_user or self.logged_user.is_active is False:
                self.logged_user = None
                raise ValidationError("Väärä käyttäjätunnus tai salasana!")
        return cleaned_data

    def login(self, request: HttpRequest) -> None:
        auth.login(request, self.logged_user)


class ProfileForm(forms.ModelForm):  # type: ignore[type-arg]
    otherinfo = forms.CharField(
        widget=forms.Textarea(),
        label="Muut yhteystiedot",
        help_text="Muut yhteystiedot, mm. IRC-nick & verkko, jne.",
        required=False,
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Init
        self.user: User | None = kwargs.pop("user", None)
        super(ProfileForm, self).__init__(*args, **kwargs)

        # Find profile
        try:
            self.profile = Profile.objects.get(user=self.user)
        except Profile.DoesNotExist:
            self.profile = Profile(user=self.user, otherinfo="")
            self.profile.save()

        # Build form
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Käyttäjäprofiili",
                "first_name",
                "last_name",
                "email",
                "otherinfo",
                ButtonHolder(Submit("submit-profile", "Tallenna")),
            )
        )

        # Finnish labels
        self.fields["first_name"].label = "Etunimi"
        self.fields["last_name"].label = "Sukunimi"
        self.fields["email"].label = "Sähköposti"
        self.fields["email"].required = True
        self.fields["otherinfo"].initial = self.profile.otherinfo

    def save(self, commit: bool = True) -> User:
        super(ProfileForm, self).save()
        self.profile.otherinfo = self.cleaned_data["otherinfo"]
        self.profile.save()
        instance: User = self.instance
        return instance

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
