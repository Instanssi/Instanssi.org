from datetime import datetime, timedelta, timezone

from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Fieldset, Layout, Submit
from django import forms
from django.contrib.auth.models import Group, User
from django.forms import widgets
from knox.crypto import create_token_string, hash_token
from knox.models import AuthToken
from knox.settings import CONSTANTS


class ApiApplicationForm(forms.Form):
    token = forms.CharField(
        max_length=64,
        min_length=64,
        initial=create_token_string,
        widget=widgets.TextInput({"readonly": "readonly"}),
    )
    expiry = forms.DateTimeField(initial=datetime.now(timezone.utc) + timedelta(days=30))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(ApiApplicationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Luo API token",
                "token",
                "expiry",
                ButtonHolder(Submit("submit", "Luo")),
            )
        )

    def save(self, commit: bool = True) -> AuthToken:
        token = AuthToken()
        token.user = self.user
        token.digest = hash_token(self.cleaned_data["token"])
        token.token_key = self.cleaned_data["token"][: CONSTANTS.TOKEN_KEY_LENGTH]
        token.expiry = self.cleaned_data["expiry"]
        token.save(commit)
        return token


class UserCreationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Lisää pääkäyttäjä",
                "username",
                "first_name",
                "last_name",
                "password",
                "email",
                ButtonHolder(Submit("submit", "Tallenna")),
            )
        )
        self.fields["password"].help_text = "Salasanan tulee olla vähintään 8 merkkiä pitkä."

    def clean_password(self):
        # Make sure password is okay
        password = self.cleaned_data["password"]
        if len(password) < 8:
            raise forms.ValidationError("Salasanan tulee olla vähintään 8 merkkiä pitkä!")
        return password

    def save(self, commit=False):
        username = self.cleaned_data["username"]
        email = self.cleaned_data["email"]
        password = self.cleaned_data["password"]
        user = User.objects.create_user(username, email, password)
        user.is_staff = True
        user.is_superuser = False
        user.is_active = True
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        # Autocreate the staff_defaults group if it doesn't exist at this point
        try:
            grp = Group.objects.get(name="staff_defaults")
        except Group.DoesNotExist:
            grp = Group(name="staff_defaults")
            grp.save()

        user.groups.add(grp)
        user.save()

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "password", "email")


class UserEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Muokkaa käyttäjää",
                "first_name",
                "last_name",
                "email",
                "is_active",
                "is_staff",
                "groups",
                ButtonHolder(Submit("submit", "Tallenna")),
            )
        )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "groups", "is_staff", "is_active")
