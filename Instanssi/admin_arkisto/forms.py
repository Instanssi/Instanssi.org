# -*- coding: utf-8 -*-

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder
from Instanssi.arkisto.models import OtherVideo, OtherVideoCategory
import urlparse


class VideoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Initialize
        self.event = kwargs.pop('event', None)
        super(VideoForm, self).__init__(*args, **kwargs)
        
        # Set choices
        if self.event:
            cats = []
            for cat in OtherVideoCategory.objects.filter(event=self.event):
                cats.append((cat.id, cat.name))
            self.fields['category'].choices = cats
        
        # Set form
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Muu Video',
                'name',
                'category',
                'description',
                'youtube_url',
                ButtonHolder (
                    Submit('submit', u'Tallenna')
                )
            )
        )
        
    def clean_youtube_url(self):
        # Make sure field has content
        if not self.cleaned_data['youtube_url']:
            return self.cleaned_data['youtube_url']
        
        # Check if we already have a valid embed url
        url = self.cleaned_data['youtube_url']
        if url.find('http://www.youtube.com/v/') == 0:
            return url
        if url.find('https://www.youtube.com/v/') == 0:
            return url

        # Parse querystring to find video ID
        parsed = urlparse.urlparse(url)
        qs = urlparse.parse_qs(parsed.query)
        
        # Check if the video id exists in query string
        if 'v' not in qs:
            raise forms.ValidationError(u'Osoitteesta ei löytynyt videotunnusta.')
            
        # All done. Return valid url
        return 'https://www.youtube.com/v/'+qs['v'][0]+'/'

    class Meta:
        model = OtherVideo
        fields = ('category', 'name', 'description', 'youtube_url')


class VideoCategoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(VideoCategoryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Kategoria',
                'name',
                ButtonHolder (
                    Submit('submit', u'Tallenna')
                )
            )
        )
                
    class Meta:
        model = OtherVideoCategory
        fields = ('name',)
