# -*- coding: utf-8 -*-

from django import forms
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder
from Instanssi.screenshow.models import Sponsor,Message,IRCMessage,PlaylistVideo
import os
import urlparse

class PlaylistVideoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PlaylistVideoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Video',
                'name',
                'url',
                'index',
                ButtonHolder (
                    Submit('submit', u'Tallenna')
                )
            )
        )
        
    def clean_url(self):
        # Check if we already have a valid embed url
        url = self.cleaned_data['url']
        if url.find('http://www.youtube.com/v/') == 0:
            return url

        # Parse querystring to find video ID
        parsed = urlparse.urlparse(url)
        qs = urlparse.parse_qs(parsed.query)
        
        # Check if the video id exists in query string
        if 'v' not in qs:
            raise ValidationError(u'Osoitteesta ei löytynyt videotunnusta.')
            
        # All done. Return valid url
        return 'http://www.youtube.com/v/'+qs['v'][0]+'/'
        
    class Meta:
        model = PlaylistVideo
        fields = ('name','url','index')

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