# -*- coding: utf-8 -*-

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder

class KeyScanForm(forms.Form):
    key = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(KeyScanForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'',
                'key',
                ButtonHolder (
                    Submit('submit', u'OK')
                )
            )
        )

