# -*- coding: utf-8 -*-

from django import forms
from uni_form.helper import FormHelper
from uni_form.layout import Submit, Layout, Fieldset, ButtonHolder
from django.contrib.auth.models import User

class UserCreationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Lisää pääkäyttäjä',
                'username',
                'first_name',
                'last_name',
                'password',
                'email',
                ButtonHolder (
                    Submit('submit', 'Tallenna')
                )
            )
        )
        self.fields['password'].help_text = u"Salasanan tulee olla vähintään 8 merkkiä pitkä."
    
    def clean_password(self):
        # Make sure password is okay
        password = self.cleaned_data['password']
        if len(password) < 8:
            raise forms.ValidationError(u'Salasanan tulee olla vähintään 8 merkkiä pitkä!')
        return password
    
    def save(self):
        username = self.cleaned_data['username']
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        user = User.objects.create_user(username, email, password)
        user.is_staff = True
        user.is_superuser = False
        user.is_active = True
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        
    class Meta:
        model = User
        fields = ('username','first_name','last_name','password','email')

class UserEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Muokkaa käyttäjää',
                'first_name',
                'last_name',
                'email',
                ButtonHolder (
                    Submit('submit', 'Tallenna')
                )
            )
        )
        
    class Meta:
        model = User
        fields = ('first_name','last_name','email')