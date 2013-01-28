# -*- coding: utf-8 -*-

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder
from Instanssi.store.models import StoreItem


class StoreItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StoreItemForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Tuote',
                'event',
                'name',
                'description',
                'price',
                'max',
                'available',
                'max_per_order',
                'delivery_type',
                'imagefile_original',
                ButtonHolder(
                    Submit('submit', u'Tallenna')
                )
            )
        )

    class Meta:
        model = StoreItem
        exclude = ('imagefile_thumbnail')
