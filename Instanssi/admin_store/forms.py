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
                'imagefile_original',
                ButtonHolder (
                    Submit('submit', u'Tallenna')
                )
            )
        )
        
    class Meta:
        model = StoreItem
        exclude = ('imagefile_thumbnail')
        
class StoreItemEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StoreItemEditForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Tuote',
                'event',
                'name',
                'description',
                'price',
                'available',
                'imagefile_original',
                ButtonHolder (
                    Submit('submit', u'Tallenna')
                )
            )
        )
        
    class Meta:
        model = StoreItem
        exclude = ('imagefile_thumbnail','max')