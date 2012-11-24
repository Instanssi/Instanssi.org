# -*- coding: utf-8 -*-

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder

class TimingForm(forms.Form):
    moveby = forms.TimeField(label=u'Kuinka paljon tapahtumia siirretään')
    direction = forms.ChoiceField(label=u'Siirron suunta', choices=[(0, u'Taaksepäin'), (1, u'Eteenpäin')])
    
    def __init__(self, *args, **kwargs):
        super(TimingForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Ajastus',
                'moveby',
                'direction',
                ButtonHolder (
                    Submit('submit', u'Muuta')
                )
            )
        )
