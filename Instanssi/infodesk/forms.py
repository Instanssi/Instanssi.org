# -*- coding: utf-8 -*-

from django import forms
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder
from Instanssi.tickets.models import Ticket
from Instanssi.store.models import StoreTransaction

class TicketKeyScanForm(forms.Form):
    key = forms.CharField(label=u'Tunniste')

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event', None)
        super(TicketKeyScanForm, self).__init__(*args, **kwargs)
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

    def clean_key(self):
        key = self.cleaned_data['key']
        try:
            self.ticket = Ticket.objects.get(event=self.event, key=key)
        except Ticket.DoesNotExist:
            raise ValidationError(u'Virheellinen lippuavain!')
        return key
    
    
class TransactionKeyScanForm(forms.Form):
    key = forms.CharField(label=u'Tunniste')

    def __init__(self, *args, **kwargs):
        super(TransactionKeyScanForm, self).__init__(*args, **kwargs)
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

    def clean_key(self):
        key = self.cleaned_data['key']
        try:
            self.transaction = StoreTransaction.objects.get(key=key)
        except StoreTransaction.DoesNotExist:
            raise ValidationError(u'Virheellinen ostos-avain!')
        return key
    