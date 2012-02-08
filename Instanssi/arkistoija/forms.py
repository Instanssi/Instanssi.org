# -*- coding: utf-8 -*-

from django import forms
from uni_form.helper import FormHelper
from uni_form.layout import Submit, Layout, Fieldset, ButtonHolder
from django.core.exceptions import ValidationError
import os

class EventForm(forms.Form):
    name = forms.CharField(label=u'Nimi', max_length=32)
    date = forms.DateField(label=u'Päivämäärä')
    
    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'date',
        )
