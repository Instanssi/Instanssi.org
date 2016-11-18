# -*- coding: utf-8 -*-

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder
from Instanssi.arkisto.models import OtherVideo, OtherVideoCategory
from Instanssi.common.misc import parse_youtube_video_id


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
                'Muu Video',
                'name',
                'category',
                'description',
                'youtube_url',
                ButtonHolder (
                    Submit('submit', 'Tallenna')
                )
            )
        )
        
    def clean_youtube_url(self):
        # Make sure field has content
        if not self.cleaned_data['youtube_url']:
            return self.cleaned_data['youtube_url']

        # Parse video id
        video_id = parse_youtube_video_id(self.cleaned_data['youtube_url'])

        # Warn if something is wrong
        if not video_id:
            raise forms.ValidationError('Osoitteesta ei löytynyt videotunnusta.')

        # Return a new video url
        return 'https://www.youtube.com/v/{}'.format(video_id)

    class Meta:
        model = OtherVideo
        fields = ('category', 'name', 'description', 'youtube_url')


class VideoCategoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(VideoCategoryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Kategoria',
                'name',
                ButtonHolder (
                    Submit('submit', 'Tallenna')
                )
            )
        )
                
    class Meta:
        model = OtherVideoCategory
        fields = ('name',)
