from django import forms
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder
from Instanssi.screenshow.models import *
from urllib.parse import urlparse


class ScreenConfigForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ScreenConfigForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Asetukset',
                'enable_videos',
                'enable_twitter',
                'enable_irc',
                'video_interval',
                ButtonHolder(
                    Submit('submit', 'Tallenna')
                )
            )
        )
        
    class Meta:
        model = ScreenConfig
        fields = ('enable_videos', 'enable_twitter', 'enable_irc', 'video_interval')


class PlaylistVideoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PlaylistVideoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Video',
                'name',
                'url',
                'index',
                ButtonHolder(
                    Submit('submit', 'Tallenna')
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
            raise ValidationError('Osoitteesta ei löytynyt videotunnusta.')
            
        # All done. Return valid url
        return 'http://www.youtube.com/v/'+qs['v'][0]+'/'
        
    class Meta:
        model = PlaylistVideo
        fields = ('name', 'url', 'index')


class IRCMessageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(IRCMessageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'IRC-Viesti',
                'nick',
                'date',
                'message',
                ButtonHolder(
                    Submit('submit', 'Tallenna')
                )
            )
        )
        
    class Meta:
        model = IRCMessage
        fields = ('nick', 'message', 'date')


class MessageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Viesti',
                'show_start',
                'show_end',
                'text',
                ButtonHolder(
                    Submit('submit', 'Tallenna')
                )
            )
        )
        
    class Meta:
        model = Message
        fields = ('show_start', 'show_end', 'text')


class SponsorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SponsorForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Sponsori',
                'name',
                'logo',
                ButtonHolder(
                    Submit('submit', 'Tallenna')
                )
            )
        )
        
    class Meta:
        model = Sponsor
        fields = ('name', 'logo')
