from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Fieldset, Layout, Submit
from django import forms
from django.contrib import auth
from django.core.exceptions import ValidationError

from Instanssi.common.misc import get_url_local_path
from Instanssi.users.models import User


class DjangoLoginForm(forms.Form):
    username = forms.CharField(label="Käyttäjätunnus")
    password = forms.CharField(label="Salasana", widget=forms.PasswordInput)
    next = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        self.next_page = kwargs.pop("next", "")
        self.logged_user = None
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

    def clean_next(self):
        return get_url_local_path(self.cleaned_data["next"])

    def clean(self):
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

    def login(self, request):
        auth.login(request, self.logged_user)


class ProfileForm(forms.ModelForm):
    otherinfo = forms.CharField(
        widget=forms.Textarea(),
        label="Muut yhteystiedot",
        help_text="Muut yhteystiedot, mm. IRC-nick & verkko, jne.",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

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

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "otherinfo")
