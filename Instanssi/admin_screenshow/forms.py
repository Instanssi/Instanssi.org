# -*- coding: utf-8 -*-

from django import forms
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder
from Instanssi.screenshow.models import Sponsor,Message,IRCMessage
import os

class IRCMessageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(IRCMessageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'IRC-Viesti',
                'nick',
                'date',
                'message',
                ButtonHolder (
                    Submit('submit', u'Tallenna')
                )
            )
        )
        
    class Meta:
        model = IRCMessage
        fields = ('nick','message','date')

class MessageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Viesti',
                'show_start',
                'show_end',
                'text',
                ButtonHolder (
                    Submit('submit', u'Tallenna')
                )
            )
        )
        
    class Meta:
        model = Message
        fields = ('show_start','show_end','text')

class SponsorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SponsorForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Sponsori',
                'name',
                'logo',
                ButtonHolder (
                    Submit('submit', u'Tallenna')
                )
            )
        )
        
    class Meta:
        model = Sponsor
        fields = ('name','logo')