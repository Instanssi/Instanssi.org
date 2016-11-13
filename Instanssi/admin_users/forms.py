# -*- coding: utf-8 -*-

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder
from django.contrib.auth.models import User, Group
from oauth2_provider.models import Application


class ApiApplicationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ApiApplicationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Lisää applikaatio',
                'name',
                'client_id',
                'client_secret',
                ButtonHolder(
                    Submit('submit', 'Lisää')
                )
            )
        )

    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name) < 4:
            raise forms.ValidationError('Nimen tulee olla vähintään 4 merkkiä pitkä!')
        return name

    def save(self, commit=True):
        app = Application(**self.cleaned_data)
        app.authorization_grant_type = Application.GRANT_CLIENT_CREDENTIALS
        app.user = self.user
        app.client_type = Application.CLIENT_CONFIDENTIAL
        app.save(commit)
        return app

    class Meta:
        model = Application
        fields = ('name', 'client_id', 'client_secret')


class UserCreationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Lisää pääkäyttäjä',
                'username',
                'first_name',
                'last_name',
                'password',
                'email',
                ButtonHolder(
                    Submit('submit', 'Tallenna')
                )
            )
        )
        self.fields['password'].help_text = "Salasanan tulee olla vähintään 8 merkkiä pitkä."
    
    def clean_password(self):
        # Make sure password is okay
        password = self.cleaned_data['password']
        if len(password) < 8:
            raise forms.ValidationError('Salasanan tulee olla vähintään 8 merkkiä pitkä!')
        return password
    
    def save(self, commit=False):
        username = self.cleaned_data['username']
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        user = User.objects.create_user(username, email, password)
        user.is_staff = True
        user.is_superuser = False
        user.is_active = True
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        # Autocreate the staff_defaults group if it doesn't exist at this point
        try:
            grp = Group.objects.get(name='staff_defaults')
        except Group.DoesNotExist:
            grp = Group(name='staff_defaults')
            grp.save()
        
        user.groups.add(grp)
        user.save()
        
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password', 'email')


class UserEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Muokkaa käyttäjää',
                'first_name',
                'last_name',
                'email',
                'is_active',
                'is_staff',
                'groups',
                ButtonHolder(
                    Submit('submit', 'Tallenna')
                )
            )
        )
        
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'groups', 'is_staff', 'is_active')
