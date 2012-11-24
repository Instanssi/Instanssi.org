# -*- coding: utf-8 -*-

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder

class TimingForm(forms.Form):
    moveby = forms.TimeField(label=u'Kuinka paljon tapahtumia siirretään')
    direction = forms.ChoiceField(label=u'Siirron suunta', choices=[(0, u'Taaksepäin'), (1, u'Eteenpäin')])
