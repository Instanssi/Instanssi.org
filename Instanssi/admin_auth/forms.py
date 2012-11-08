# -*- coding: utf-8 -*-

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder

class LoginForm(forms.Form):
    username = forms.CharField(label=u"Käyttäjätunnus", help_text=u"Admin-paneelin käyttäjätunnuksesi. Huom! OpenID-tunnukset eivät kelpaa!")
    password = forms.CharField(label=u"Salasana", widget=forms.PasswordInput)
    
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'',
                'username',
                'password',
                ButtonHolder (
                    Submit('submit', u'Kirjaudu')
                )
            )
        )
