# -*- coding: utf-8 -*-

from django import forms
from django.shortcuts import get_object_or_404
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder
from datetime import datetime
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from Instanssi.kompomaatti.models import Compo, Entry, VoteCode, VoteCodeRequest, Event, Competition, CompetitionParticipation
import urlparse

class AdminCompetitionScoreForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.competition = kwargs.pop('competition', None)
        
        # Init
        super(AdminCompetitionScoreForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout()
        
        # Create a fieldset for everything
        fs = Fieldset(u'Pisteytys')
    
        # Set fields
        participants = CompetitionParticipation.objects.filter(competition=self.competition)
        for p in participants:
            name = str(p.id)
            self.fields[name] = forms.FloatField()
            self.fields[name].label = p.participant_name
            self.fields[name].help_text = u'Osallistujan '+p.participant_name+u' saavuttama tulos.'
            self.fields[name].initial = p.score
            fs.fields.append(name)
    
        # Add buttonholder
        bh = ButtonHolder (
            Submit('submit', u'Tallenna')
        )
        fs.fields.append(bh)
        
        # Add fieldset to layout
        self.helper.layout.fields.append(fs)
        
    def save(self):
        for k,v in self.cleaned_data.iteritems():
            p = get_object_or_404(CompetitionParticipation, pk=int(k))
            p.score = v
            p.save()

class AdminParticipationEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AdminParticipationEditForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Osallistuja',
                'participant_name',
                'score',
                'disqualified',
                'disqualified_reason',
                ButtonHolder (
                    Submit('submit', 'Tallenna')
                )
            )
        )
        
    class Meta:
        model = CompetitionParticipation
        fields = ('participant_name','score','disqualified','disqualified_reason')

class AdminCompetitionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AdminCompetitionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Kilpailu',
                'name',
                'description',
                'participation_end',
                'start',
                'end',
                'score_type',
                'score_sort',
                'show_results',
                'hide_from_archive',
                'active',
                ButtonHolder (
                    Submit('submit', 'Tallenna')
                )
            )
        )
        
    class Meta:
        model = Competition
        exclude = ('event',)

class AdminCompoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AdminCompoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Kompo',
                'name',
                'description',
                'adding_end',
                'editing_end',
                'compo_start',
                'voting_start',
                'voting_end',
                'entry_sizelimit',
                'source_sizelimit',
                'formats',
                'source_formats',
                'active',
                'show_voting_results',
                'entry_view_type',
                'hide_from_archive',
                ButtonHolder (
                    Submit('submit', 'Tallenna')
                )
            )
        )
        
    class Meta:
        model = Compo
        exclude = ('event',)

class AdminEntryAddForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Initialize
        self.event = kwargs.pop('event', None)
        super(AdminEntryAddForm, self).__init__(*args, **kwargs)
        
        # Set choices
        if self.event:
            compos = []
            for compo in Compo.objects.filter(event=self.event):
                compos.append((compo.id, compo.name))
            self.fields['compo'].choices = compos
        
        # Set form
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Tuotos',
                'user',
                'compo',
                'name',
                'description',
                'creator',
                'entryfile',
                'sourcefile',
                'imagefile_original',
                'youtube_url',
                ButtonHolder (
                    Submit('submit', 'Lisää')
                )
            )
        )
        
    class Meta:
        model = Entry
        exclude = ('disqualified','disqualified_reason','imagefile_thumbnail','imagefile_medium','archive_score','archive_rank')

class AdminEntryEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Initialize
        self.event = kwargs.pop('event', None)
        super(AdminEntryEditForm, self).__init__(*args, **kwargs)
        
        # Set choices for Compo field
        if self.event:
            compos = []
            for compo in Compo.objects.filter(event=self.event):
                compos.append((compo.id, compo.name))
            self.fields['compo'].choices = compos
        
        # Set form
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Tuotos',
                'compo',
                'user',
                'name',
                'description',
                'creator',
                'entryfile',
                'sourcefile',
                'imagefile_original',
                'youtube_url',
                'disqualified',
                'disqualified_reason',
                ButtonHolder (
                    Submit('submit', 'Tallenna')
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

        # Parse querystring to find video ID
        parsed = urlparse.urlparse(url)
        qs = urlparse.parse_qs(parsed.query)
        
        # Check if the video id exists in query string
        if 'v' not in qs:
            raise ValidationError(u'Osoitteesta ei löytynyt videotunnusta.')
            
        # All done. Return valid url
        return 'http://www.youtube.com/v/'+qs['v'][0]+'/'

    class Meta:
        model = Entry
        exclude = ('imagefile_thumbnail','imagefile_medium','archive_score','archive_rank')

class CreateTokensForm(forms.Form):
    amount = forms.IntegerField(min_value=1, max_value=100, label=u"Määrä", help_text=u"Montako tokenia luodaan.")
    
    def __init__(self, *args, **kwargs):
        super(CreateTokensForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Generoi tokeneita',
                'amount',
                ButtonHolder (
                    Submit('submit', 'Generoi')
                )
            )
        )

