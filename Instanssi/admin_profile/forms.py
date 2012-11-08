# -*- coding: utf-8 -*-

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder
from django.contrib.auth.models import User

class InformationChangeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(InformationChangeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'',
                'first_name',
                'last_name',
                'email',
                ButtonHolder (
                    Submit('submit', u'Tallenna')
                )
            )
        )
        
        self.fields['email'].required = True
        
    class Meta:
        model = User
        fields = ('first_name','last_name','email')

class PasswordChangeForm(forms.Form):
    old_pw = forms.CharField(widget=forms.PasswordInput, label=u'Vanha salasana', help_text=u'Kirjoita vanha salasanasi turvallisuussyistä.')
    new_pw = forms.CharField(widget=forms.PasswordInput, label=u'Uusi salasana', help_text=u'Kirjoita uusi salasanasi. Tulee olla vähintään 8 merkkiä pitkä.')
    new_pw_again = forms.CharField(widget=forms.PasswordInput, label=u'Uusi salasana uudelleen', help_text=u'Kirjoita uusi salasanasi toistamiseen varmistukseksi.')
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'',
                'old_pw',
                'new_pw',
                'new_pw_again',
                ButtonHolder (
                    Submit('submit', u'Tallenna')
                )
            )
        )
        
    def save(self):
        password = self.cleaned_data['new_pw']
        self.user.set_password(password)
        self.user.save()
        
    def clean_old_pw(self):
        # Make sure this is valid
        old = self.cleaned_data['old_pw']
        if not self.user.check_password(old):
            raise forms.ValidationError(u'Vanha salasana väärin!')
            
        # Remember to return cleaned data
        return old
        
    def clean_new_pw(self):
        pw = self.cleaned_data['new_pw']
        if len(pw) < 8:
            raise forms.ValidationError(u'Salasanan tulee olla vähintään 8 merkkiä pitkä!')
        return pw
        
    def clean_new_pw_again(self):
        pw = self.cleaned_data['new_pw_again']
        if len(pw) < 8:
            raise forms.ValidationError(u'Salasanan tulee olla vähintään 8 merkkiä pitkä!')
        return pw
        
    def clean(self):
        cleaned_data = super(PasswordChangeForm, self).clean()
        
        # Make sure new pw fields match
        pwa = cleaned_data.get('new_pw')
        pwb = cleaned_data.get('new_pw_again')
        if pwa != pwb:
            msg = u'Salasana ei vastaa edelliseen kenttään annettua!'
            self._errors["new_pw_again"] = self.error_class([msg])
            del cleaned_data["new_pw_again"]
                
        # Remember to return cleaned data
        return cleaned_data
    
