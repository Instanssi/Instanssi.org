# -*- coding: utf-8 -*-

from django import forms
from uni_form.helper import FormHelper
from uni_form.layout import Submit, Layout, Fieldset, ButtonHolder
from datetime import datetime
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from Instanssi.kompomaatti.models import Compo, Entry, VoteCode, VoteCodeRequest, Event
from Instanssi.dbsettings.models import Setting

class AdminChangeEventForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        
        # Init
        super(AdminChangeEventForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout()
        
        # Get settings in group
        ev_objs = Event.objects.all()
        events = [(-1,u'Ei mitään')]
        for ev in ev_objs:
            events.append((ev.id, ev.name))
        
        # Get initial value
        initial = None
        if self.request != None and 'm_event_id' in self.request.session:
            initial = self.request.session['m_event_id']
        elif len(events) > 0:
            initial = Setting.get('active_event_id', 'events', events[0])
        
        # Create fieldset for everything
        fs = Fieldset(u'Asetukset')

        # Add fields for settings
        self.fields['m_event_id'] = forms.TypedChoiceField(choices=events, coerce=int)
        self.fields['m_event_id'].help_text = u'Valitsee kompomaatin admin-paneelissa käsiteltävänä olevan tapahtuman. Vaikuttaa kaikkiin kompomaatti-menun alaisiin sivuihin! Tämä asetus ei tee muutoksia tietokantaan.'
        self.fields['m_event_id'].label = u'Tapahtuman valinta'
        if initial:
            self.fields['m_event_id'].initial = initial

        # Add buttonholder
        self.helper.layout = Layout(
            Fieldset(
                u'Tapahtuman valinta',
                'm_event_id',
                ButtonHolder (
                    Submit('submit', 'Valitse')
                )
            )
        )
        
    def save(self):
        self.request.session['m_event_id'] = self.cleaned_data['m_event_id']


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

class AdminEntryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AdminEntryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Tuotos',
                'compo',
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
        
    class Meta:
        model = Entry
        exclude = ('user','imagefile_thumbnail','imagefile_medium','archive_score','archive_rank')

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
        
class RequestVoteCodeForm(forms.ModelForm):
    formtype = forms.CharField(widget=forms.HiddenInput(),initial=u"requestvotecodeform")
    
    def __init__(self, *args, **kwargs):
        super(RequestVoteCodeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Pyydä äänestysoikeutta',
                'text',
                'formtype',
                ButtonHolder (
                    Submit('submit', 'Pyydä äänestysoikeutta')
                )
            )
        )
        
    class Meta:
        model = VoteCodeRequest
        fields = ('text',)
        
class VoteCodeAssocForm(forms.Form):
    formtype = forms.CharField(widget=forms.HiddenInput(),initial=u"votecodeassocform")
    code = forms.CharField(max_length=8, label=u"Äänestyskoodi", help_text=u"Syötä saamasi äänestyskoodi tähän.")
    
    def __init__(self, *args, **kwargs):
        super(VoteCodeAssocForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Syötä äänestyskoodi',
                'code',
                'formtype',
                ButtonHolder (
                    Submit('submit', 'Tallenna')
                )
            )
        )
        
    def clean_code(self):
        code = self.cleaned_data['code']
        try:
            vc = VoteCode.objects.get(key=code)
        except VoteCode.DoesNotExist:
            raise ValidationError(u'Äänestyskoodia ei ole olemassa!')
        return code
