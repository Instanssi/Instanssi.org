# -*- coding: utf-8 -*-

from django.forms import ModelForm
from models import Compo, Entry
from uni_form.helper import FormHelper
from uni_form.layout import Submit, Layout, Fieldset, ButtonHolder
from datetime import datetime

class EntryForm(ModelForm):
    def __init__(self, *args, **kwargs):
        legend = kwargs.pop('legend', 'Entry')
        compo = kwargs.pop('compo', None)
        editing = kwargs.pop('editing', False)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                legend,
                'name',
                'creator',
                'description',
                'entryfile',
                'sourcefile',
                'imagefile_original',
                ButtonHolder (
                    Submit('submit', 'Tallenna')
                )
            )
        )
        super(EntryForm, self).__init__(*args, **kwargs) 
        if compo:
            self.fields['entryfile'].help_text = u"Tuotospaketti. Sallitut tiedostoformaatit: " + compo.readable_allowed_entry_formats() + '.';
            self.fields['sourcefile'].help_text = u"Lähdekoodipaketti. Sallitut tiedostoformaatit: " + compo.readable_allowed_source_formats() + '.';
        if editing:
            self.fields['entryfile'].required = False

    class Meta:
        model = Entry
        fields = ('name','creator','description','entryfile','sourcefile','imagefile_original')
