# -*- coding: utf-8 -*-

from django import forms
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder
from Instanssi.store.models import StoreTransaction, TransactionItem


class ItemKeyScanForm(forms.Form):
    key = forms.CharField(label=u'Tunniste')

    def __init__(self, *args, **kwargs):
        super(ItemKeyScanForm, self).__init__(*args, **kwargs)
        self.item = None
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'',
                'key',
                ButtonHolder(
                    Submit('submit', u'OK')
                )
            )
        )

    def clean_key(self):
        key = self.cleaned_data['key']
        try:
            self.item = TransactionItem.objects.get(key=key)
        except TransactionItem.DoesNotExist:
            raise ValidationError(u'Virheellinen tuoteavain!')
        return key


class TransactionKeyScanForm(forms.Form):
    key = forms.CharField(label=u'Tunniste')

    def __init__(self, *args, **kwargs):
        super(TransactionKeyScanForm, self).__init__(*args, **kwargs)
        self.transaction = None
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'',
                'key',
                ButtonHolder(
                    Submit('submit', u'OK')
                )
            )
        )

    def clean_key(self):
        key = self.cleaned_data['key']
        try:
            self.transaction = StoreTransaction.objects.get(key=key)
        except StoreTransaction.DoesNotExist:
            raise ValidationError(u'Virheellinen transaktioavain!')
        return key
